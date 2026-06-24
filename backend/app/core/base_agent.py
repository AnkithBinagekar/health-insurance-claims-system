import time
import traceback
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from backend.app.schemas.claim import ClaimContext
from backend.app.schemas.trace import AgentTrace, ConfidenceEvent
from backend.app.schemas.enums import AgentStatus
from backend.app.core.config import settings

class BaseAgent(ABC):
    
    def __init__(self):
        self.agent_name = self.__class__.__name__

    async def execute(self, context: ClaimContext) -> ClaimContext:
        if context.state.is_halted:
            self._record_skipped(context)
            return context

        trace = AgentTrace(agent_name=self.agent_name)
        start_time = time.perf_counter()

        try:
            # Dynamic simulation based on ExecutionState (Removes hardcoded agent names)
            if self.agent_name in context.state.simulate_failures_for:
                raise RuntimeError(f"Simulated component failure triggered for {self.agent_name}.")

            context = await self._process(context, trace)
            
            # If the agent didn't explicitly set status to DEGRADED, mark SUCCESS
            if trace.status == AgentStatus.PENDING:
                trace.status = AgentStatus.SUCCESS
            
        except Exception as e:
            trace.status = AgentStatus.FAILED
            trace.errors.append(str(e))
            trace.errors.append(traceback.format_exc())
            print(f"\nERROR IN {self.agent_name}")
            print(traceback.format_exc())
            # Ledger-based confidence degradation
            penalty = settings.confidence_penalty_per_failure
            penalty_event = ConfidenceEvent(
                agent_name=self.agent_name,
                penalty_applied=penalty,
                reason=f"Unhandled exception in {self.agent_name}: {str(e)}"
            )
            context.trace.confidence_ledger.append(penalty_event)
            
            trace.decision_impact = f"Agent failed. Confidence reduced by {penalty * 100}%."
            context.result.notes.append(f"System degraded: {self.agent_name} encountered an error.")
            
        finally:
            trace.end_time = datetime.now(timezone.utc)
            trace.execution_time_ms = (time.perf_counter() - start_time) * 1000
            context.trace.agent_traces.append(trace)

        return context

    @abstractmethod
    async def _process(self, context: ClaimContext, trace: AgentTrace) -> ClaimContext:
        pass

    def _record_skipped(self, context: ClaimContext) -> None:
        trace = AgentTrace(
            agent_name=self.agent_name,
            status=AgentStatus.SKIPPED,
            warnings=[f"Pipeline halted: {context.state.halt_reason}"],
            end_time=datetime.now(timezone.utc),
            execution_time_ms=0.0
        )
        context.trace.agent_traces.append(trace)