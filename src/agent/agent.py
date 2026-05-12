import typing as tp

from abc import ABC, abstractmethod
from asyncio import sleep, Semaphore
from datetime import datetime
from logging import Logger

from google import genai as ga

from .metrics import TokenType, ToolCallStatus, TokenUsage, MoneySpent, \
    CachedTokens, ToolCalls, RequestProcessingTime
from ..tools import Tool
from ..types import ToolCallContext


CO_DEFAULT_RETRIES = 3


class Agent(ABC):
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

    @abstractmethod
    async def execute(
        self,
        system_prompt: str,
        prompt: str,
        context: ToolCallContext,
    ) -> None:
        pass

    async def _try_n_times(
        self,
        callable_: tp.Callable[[], tp.Any],
        n: int = CO_DEFAULT_RETRIES
    ) -> tp.Any:
        for i in range(n):
            try:
                result = await callable_()
                if i > 0:
                    self._logger.info(f'Successful retry after {i} tries')
                return result
            except Exception:
                self._logger.exception('Exception during retrying')


class GeminiAgent(Agent):
    def __init__(
        self,
        client: ga.Client,
        model_name: str,
        tools: list[Tool],
        logger: Logger,
        generation_config: dict[str, tp.Any] | None = None,
        sleep_time: float = 0.3,
        concurrency_limit: int = 4,
    ) -> None:
        super().__init__(logger)

        self._client = client
        self._model_name = model_name
        self._tools = tools
        self._generation_config = generation_config
        self._sleep_time = sleep_time
        self._concurrency_limit = concurrency_limit

        self._name_to_tool = {
            tool.name: tool
            for tool in self._tools
        }
        self._semaphore = Semaphore(self._concurrency_limit)

    async def execute(
        self,
        system_prompt: str,
        prompt: str,
        context: ToolCallContext
    ) -> None:
        async with self._semaphore:
            processing_start = datetime.now()
            input_tokens = 0
            output_tokens = 0
            cached_tokens = 0
            interaction = await self._client.aio.interactions.create(
                model=self._model_name,
                input=prompt,
                tools=[
                    tool.description
                    for tool in self._tools
                ],
                generation_config=self._generation_config,
                system_instruction=system_prompt,
            )  # type: ignore  # pyrefly: ignore
            while True:
                usage = interaction.usage
                input_tokens += usage.total_input_tokens or 0
                output_tokens += usage.total_output_tokens or 0
                cached_tokens += usage.total_cached_tokens or 0
                if not interaction.outputs:
                    break

                (
                    should_break,
                    function_results
                ) = await self._process_interaction(interaction, context)
                if should_break:
                    break

                interaction = await self._try_n_times(
                    lambda: self._client.aio.interactions.create(
                        model=self._model_name,
                        previous_interaction_id=interaction.id,
                        input=function_results,  # type: ignore
                    )  # pyrefly: ignore
                )
                if interaction is None:
                    break

                await sleep(self._sleep_time)

        processing_finish = datetime.now()
        token_usage_labels = dict(
            model=self._model_name,
            agent_name=context.bot_name,
        )
        TokenUsage.labels(
            **token_usage_labels,
            type=TokenType.Input.value
        ).inc(input_tokens)
        TokenUsage.labels(
            **token_usage_labels,
            type=TokenType.Output.value
        ).inc(output_tokens)
        CachedTokens.labels(**token_usage_labels).inc(cached_tokens)
        RequestProcessingTime.inc(
            (processing_finish - processing_start).total_seconds()
        )

    async def _process_interaction(
        self,
        interaction: ga.interactions.Interaction,
        context: ToolCallContext,
    ) -> tuple[bool, list[dict]]:
        function_calls: list[ga.interactions.FunctionCallContent] = [
            out  # type: ignore
            for out in interaction.outputs  # type: ignore
            if out.type == 'function_call'
        ]
        if len(function_calls) == 0:
            return True, []

        function_results = []
        for output in function_calls:
            tool_name = output.name
            arguments = output.arguments

            result = await self._process_tool_call(
                tool_name, arguments, context, output
            )
            self._logger.debug(f'[{output.id}] Result: {result}')
            function_results.append({
                'type': 'function_result',
                'name': output.name,
                'call_id': output.id,
                'result': result
            })

        return False, function_results

    async def _process_tool_call(
        self,
        tool_name: str,
        arguments: dict[str, tp.Any],
        context: ToolCallContext,
        output: ga.interactions.FunctionCallContent,
    ) -> tp.Any:
        is_success = True
        if 'context' in arguments:
            arguments['new_context'] = arguments['context']
            del arguments['context']

        if tool_name not in self._name_to_tool:
            result = f'ERROR: Tool {tool_name} not found'
            is_success = False
        else:
            tool = self._name_to_tool[tool_name]
            self._logger.debug(
                f'[{output.id}; {context.chat_id}] ' +
                f'Calling {tool_name}' +
                f' with parameters: {arguments}'
            )
            try:
                result = await tool(context=context, **arguments)
                if result is None:
                    result = 'Success'
            except Exception as e:
                self._logger.exception(
                    f'Error during tool call with id {output.id}'
                )
                result = f'ERROR: {e}'
                is_success = False

        ToolCalls.labels(
            tool_name=tool_name,
            status=ToolCallStatus.from_success(is_success).value
        ).inc()

        return result
