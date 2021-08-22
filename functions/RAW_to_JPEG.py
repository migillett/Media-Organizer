import os.path
import sys
import logging

try:
    import rawpy
    import imageio
except ImportError as e:
    logging.error(f'ERROR: {e}')
    sys.exit()

logging.getLogger().setLevel(logging.INFO)

def raw_to_jpeg(source_file, destination_folder, delete_old=False):
    extensions = ('.CR2', '.ARW', '.NEF', '.CRW', '.DNG', '.TIF')
    images_processed = 0

    if source_file.endswith(extensions):

        filename = os.path.basename(source_file)
        converted_path = os.path.join(destination_folder, f'{os.path.splitext(filename)[0]}.jpg')

        if not os.path.exists(converted_path):
            with rawpy.imread(source_file) as raw:
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
                os.remove(source_file)
                logging.info(f'Deleted file: {filename}')

        else:
            logging.info(f'Image already exported: {filename}')


# if __name__ == '__main__':
#     # put the starting directory here:
#     photos_source = 'F:\\PHOTOS\\Family Photos\\189 Oakwood Dr. NW Photos\\2018-04-21_Leahs flowers_001.ARW'
#     destination_folder = 'C:\\Users\\migil\Desktop\\test'
#     raw_to_jpeg(photos_source, destination_folder, delete_old=False)
