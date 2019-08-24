import time
import os
import logging
import requests
import threading
import PIL
from PIL import Image

FORMAT = "[%(threadName)s, %(asctime)s, %(levelname)s] %(message)s"
logging.basicConfig(filename='myLogfile_threads.log', level=logging.DEBUG, format=FORMAT)

class ThumbnailMakerService(object):
    def __init__(self, home_dir='.'):
        self.home_dir = home_dir
        self.input_dir = self.home_dir + os.path.sep + 'incoming'
        self.output_dir = self.home_dir + os.path.sep + 'outgoing'
        self.abs_inp_dir = os.getcwd() + os.path.sep + 'incoming'
        self.downloaded_bytes = 0 # Introducing a shared readable resource across threads
        self.dl_lock  = threading.Lock()

    def download_image( self, url ):
        logging.info('downloading image at URL {}'.format(url))
        img_filename = str(url).split(os.path.sep)[-1]
        r            = requests.get( url )
        with open( img_filename, 'wb' ) as f:
           f.write(r.content)
           img_size = os.path.getsize(img_filename)
           with self.dl_lock: #using with stmt to ensure lock is released no matter what
                self.downloaded_bytes += img_size #this is a shared resource across mutliple threads and 
                                             #the value read can be corrupt by a given thread. Use threading locks for data synchronization
                logging.info('image-- {}[{} bytes] saved'.format(img_filename, img_size))


    def download_images(self, img_url_list):
        # validate inputs
        if not img_url_list:
            return
        os.makedirs(self.input_dir, exist_ok=True)
        
        logging.info("beginning image downloads")

        start = time.perf_counter()
        os.chdir( self.abs_inp_dir )
        threads = []
        for url in img_url_list:
            # download each image and save to the input dir 
            t = threading.Thread(target=self.download_image, args=(url,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()   
        end = time.perf_counter()

        logging.info("downloaded {} images in {} seconds".format(len(img_url_list), end - start))

    def perform_resizing(self):
        # validate inputs

        if not os.listdir(self.abs_inp_dir):
            print('In here')
            return
        os.makedirs(self.output_dir, exist_ok=True)

        logging.info("beginning image resizing")
        target_sizes = [32, 64, 200]
        num_images = len(os.listdir(self.abs_inp_dir))

        start = time.perf_counter()
        for filename in os.listdir(self.abs_inp_dir):
            orig_img = Image.open(self.abs_inp_dir + os.path.sep + filename)
            for basewidth in target_sizes:
                img = orig_img
                # calculate target height of the resized image to maintain the aspect ratio
                wpercent = (basewidth / float(img.size[0]))
                hsize = int((float(img.size[1]) * float(wpercent)))
                # perform resizing
                img = img.resize((basewidth, hsize), PIL.Image.LANCZOS)
                
                # save the resized image to the output dir with a modified file name 
                new_filename = os.path.splitext(filename)[0] + \
                    '_' + str(basewidth) + os.path.splitext(filename)[1]
                img.save(self.output_dir + os.path.sep + new_filename)

            os.remove(self.abs_inp_dir + os.path.sep + filename)
        end = time.perf_counter()

        logging.info("created {} thumbnails in {} seconds".format(num_images, end - start))

    def make_thumbnails(self, img_url_list):
        logging.info("START make_thumbnails")
        start = time.perf_counter()

        self.download_images(img_url_list) #i/o-bound operation
        os.chdir('..')
        #self.perform_resizing() #cpu-bound operation

        end = time.perf_counter()
        logging.info("END make_thumbnails in {} seconds".format(end - start))

    

