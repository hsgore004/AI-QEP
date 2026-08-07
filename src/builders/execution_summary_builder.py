from models.execution_summary import ExecutionSummary


class ExecutionSummaryBuilder:

    def build(
        self,
        ui_output,
        api_output,
        robot_output,
        report_path,
        execution_time,
        robot_result,
    ) -> ExecutionSummary:

        return ExecutionSummary(
            requirement_agent=True,
            ui_agent=True,
            api_agent=True,
            robot_agent=True,
            robot_builder=True,
            robot_execution=(robot_result.returncode == 0),
            report_path=report_path,
            ui_output=ui_output,
            api_output=api_output,
            robot_output=robot_output,
            execution_time=execution_time,
        )