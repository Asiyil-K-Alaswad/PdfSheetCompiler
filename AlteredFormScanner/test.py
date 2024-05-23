import subprocess
def execute_FormScanner(formScanner_executable, formScanner_template, images_dir, output_csv):
    """
    Executes the FormScanner for scanning the images and producing the output CSV.

    Args:
        formScanner_executable (string): The FormScanner's .jar executable path
        formScanner_template (string): The FormScanner's .xtmpl template path
        images_dir (string): The converted images' directory path
        output_csv (string): The FormScanner's csv output path

    Raises:
        subprocessfileedProcessError: Upon FormScanner execution failure
    """

    # logging.info('''Scanning images with FormScanner ...
    #     - FormScanner template: {}'''
    #     .format(formScanner_template))

    formScanner_cmd = ['java',
                            '-jar',
                            formScanner_executable,
                            formScanner_template,
                            images_dir,
                            output_csv]
    # logging.debug("Prepared FormScanner command :: {}".format(' '.join(formScanner_cmd)))
    try:
        subprocess.run(formScanner_cmd, check=True)
    except Exception:
        # logging.error("FormScanner execution failed.")
        raise 'noooo'



# execute_FormScanner(
#     'lib/formscanner-main-1.1.2.jar',
#     'template.xtmpl',
#     'images',
#     'output.csv'
# )
