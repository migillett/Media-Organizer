import os
import sys
import logging

try:
    import rawpy
    import imageio
except ImportError as e:
    logging.error(f'ERROR: {e}')
    sys.exit()

logging.getLogger().setLevel(logging.INFO)


def raw_to_jpeg(source_path, destination_path, delete_old=False):
    images_processed = 0

    filename = os.path.basename(source_path)
    converted_path = os.path.join(destination_path, f'{os.path.splitext(filename)[0]}.jpg')

    if not os.path.exists(converted_path):
        with rawpy.imread(source_path) as raw:
            rgb = raw.postprocess(
                gamma=(1.25, 4.5),
                bright=1.1,
                no_auto_bright=False,
                use_camera_wb=True
            )

        imageio.imsave(converted_path, rgb)
        logging.info(f'Converted image: {filename}')
        images_processed += 1

        if delete_old:
            os.remove(source_path)
            logging.info(f'Deleted file: {filename}')

    else:
        logging.info(f'Image already exported: {filename}')