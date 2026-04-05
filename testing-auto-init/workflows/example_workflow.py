import requests
from scriptable.base_workflow import BaseWorkflow

class Workflow(BaseWorkflow):
    name        = "Example Workflow"
    description = ""

    def setup(self, context):
        self.add_step("Step 1", self._step_one)
        self.add_step("Step 2", self._step_two)

    def _step_one(self, ctx, prior, results):
        self.info(results, "step one", detail="Add your logic here")
        return {"data": "from step one"}

    def _step_two(self, ctx, prior, results):
        # prior[-1]["result"] contains step one's return value
        self.info(results, "step two", detail="Add your logic here")
