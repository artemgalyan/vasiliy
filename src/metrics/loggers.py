from .metrics import TokenUsage, MoneySpent, CachedTokens, TokenType


class TokenLogger:
    def __init__(
        self,
        model_name: str,
        bot_name: str,
        input_token_price: float,
        output_token_price: float,
        cached_token_price: float = 0.
    ) -> None:
        self._model_name = model_name
        self._bot_name = bot_name
        self._input_token_price = input_token_price
        self._output_token_price = output_token_price
        self._cached_token_price = cached_token_price
        self.input_tokens = 0
        self.output_tokens = 0
        self.cached_tokens = 0

    def add_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
    ) -> None:
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.cached_tokens += cached_tokens

    def log_usage(
        self,
    ) -> None:
        token_usage_labels = dict(
            model=self._model_name,
            agent_name=self._bot_name,
        )
        TokenUsage.labels(
            **token_usage_labels,
            type=TokenType.Input.value
        ).inc(self.input_tokens)
        TokenUsage.labels(
            **token_usage_labels,
            type=TokenType.Output.value
        ).inc(self.output_tokens)
        CachedTokens.labels(**token_usage_labels).inc(self.cached_tokens)
        input_tokens_money_spent = round(
            (self.input_tokens - self.cached_tokens) * self._input_token_price
        )
        MoneySpent.labels(
            **token_usage_labels,
            category=TokenType.Input.value
        ).inc(input_tokens_money_spent)
        MoneySpent.labels(
            **token_usage_labels,
            category=TokenType.Cached.value
        ).inc(round(self.cached_tokens * self._cached_token_price))
        MoneySpent.labels(
            **token_usage_labels,
            category=TokenType.Output.value
        ).inc(round(self.output_tokens * self._output_token_price))
