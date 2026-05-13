from enum import Enum
from prometheus_client import Counter, Gauge


class TokenType(Enum):
    Input = 'input'
    Output = 'output'
    Cached = 'cached'


class ToolCallStatus(Enum):
    Success = 'success'
    Failure = 'failure'

    @staticmethod
    def from_success(is_success: bool):
        if is_success:
            return ToolCallStatus.Success
        return ToolCallStatus.Failure


RequestProcessingStatus = ToolCallStatus


TokenUsage = Counter(
    'token_usage',
    'Cumulative token usage',
    ['model', 'type', 'agent_name']
)
MoneySpent = Counter(
    'money_spent',
    'Amount of money spent on tokens',
    ['model', 'agent_name', 'category'],
)
CachedTokens = Counter(
    'cached_token_usage',
    'Cumulative cached token usage',
    ['model', 'agent_name']
)
ToolCalls = Counter(
    'agent_tool_calls_total',
    'Total number of times each tool was invoked',
    ['tool_name', 'status'],
)
RequestProcessingTime = Gauge(
    'request_processing_time',
    'Time needed to process a request, sec'
)
RequestsProcessed = Counter(
    'request_processed',
    'Number of request processed',
    ['agent_name', 'result'],
)
