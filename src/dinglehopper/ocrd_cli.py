from functools import cached_property
import os
from typing import Optional

import click
from ocrd_models import OcrdFileType
from ocrd import Processor
from ocrd.decorators import ocrd_cli_options, ocrd_cli_wrap_processor
from ocrd_utils import make_file_id

from .cli import process as cli_process

@click.command()
@ocrd_cli_options
def ocrd_dinglehopper(*args, **kwargs):
    return ocrd_cli_wrap_processor(OcrdDinglehopperEvaluate, *args, **kwargs)

class OcrdDinglehopperEvaluate(Processor):

    @cached_property
    def executable(self):
        return 'ocrd-dinglehopper'

    def process_page_file(self, *input_files: Optional[OcrdFileType]) -> None:

        assert self.parameter
        metrics = self.parameter["metrics"]
        textequiv_level = self.parameter["textequiv_level"]

        try:
            gt_file, ocr_file = input_files
            assert gt_file, 'missing GT file'
            assert ocr_file, 'missing OCR file'
            assert gt_file.local_filename
            assert ocr_file.local_filename
        except (ValueError, AssertionError) as err:
            self.logger.warning(f'Missing either GT file, OCR file or both: {err}') # TODO how to log which page?
            return

        page_id = gt_file.pageId

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
