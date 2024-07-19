import json
import os

import click
import importlib_resources
from ocrd import Processor
from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from ocrd_utils import assert_file_grp_cardinality, getLogger, make_file_id

from .cli import process as cli_process

OCRD_TOOL = json.loads(
    importlib_resources.files(__name__)
    .joinpath("ocrd-tool.json")
    .read_text(encoding="utf-8", errors="strict")
)


@click.command()
@ocrd_cli_options
def ocrd_dinglehopper(*args, **kwargs):
    return ocrd_cli_wrap_processor(OcrdDinglehopperEvaluate, *args, **kwargs)


class OcrdDinglehopperEvaluate(Processor):
    def __init__(self, *args, **kwargs):
        kwargs["ocrd_tool"] = OCRD_TOOL["tools"]["ocrd-dinglehopper"]
        kwargs["version"] = OCRD_TOOL["version"]
        super(OcrdDinglehopperEvaluate, self).__init__(*args, **kwargs)

    def process(self):
        assert_file_grp_cardinality(self.input_file_grp, 2, "GT and OCR")
        assert_file_grp_cardinality(self.output_file_grp, 1)

        log = getLogger("processor.OcrdDinglehopperEvaluate")

        metrics = self.parameter["metrics"]
        textequiv_level = self.parameter["textequiv_level"]
        gt_grp, ocr_grp = self.input_file_grp.split(",")

        input_file_tuples = self.zip_input_files(on_error="abort")
        for n, (gt_file, ocr_file) in enumerate(input_file_tuples):
            if not gt_file or not ocr_file:
                # file/page was not found in this group
                continue
            gt_file = self.workspace.download_file(gt_file)
            ocr_file = self.workspace.download_file(ocr_file)
            page_id = gt_file.pageId

            log.info("INPUT FILES %i / %s↔ %s", n, gt_file, ocr_file)

            file_id = make_file_id(ocr_file, self.output_file_grp)
            report_prefix = os.path.join(self.output_file_grp, file_id)

            # Process the files
            try:
                os.mkdir(self.output_file_grp)
            except FileExistsError:
                pass
            cli_process(
                gt_file.local_filename,
                ocr_file.local_filename,
                report_prefix,
                metrics=metrics,
                textequiv_level=textequiv_level,
            )

            # Add reports to the workspace
            for report_suffix, mimetype in [
                [".html", "text/html"],
                [".json", "application/json"],
            ]:
                self.workspace.add_file(
                    file_id=file_id + report_suffix,
                    file_grp=self.output_file_grp,
                    page_id=page_id,
                    mimetype=mimetype,
                    local_filename=report_prefix + report_suffix,
                )


if __name__ == "__main__":
    ocrd_dinglehopper()
