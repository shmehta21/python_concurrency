##################################
#Python Queue supports blocking API calls. Supports the following methods
# put -> Puts an item into the queue.
# get -> Removes an item . Blocks till and item is available on the queue
# task_done -> Marks an item as gotten/processed once it is consumed from the queue
# join -> Blocks until all the items in the queue have been processed
##################################


import time
import os
import logging
import requests
import PIL
from PIL import Image
from queue import Queue
from threading import Thread

FORMAT = "[%(threadName)s, %(asctime)s, %(levelname)s] %(message)s"
logging.basicConfig(filename='myLogfile_queue.log', level=logging.DEBUG, format=FORMAT)

class ThumbnailMakerService(object):
    def __init__(self, home_dir='.'):
        self.home_dir = home_dir
        self.input_dir = self.home_dir + os.path.sep + 'incoming'
        self.output_dir = self.home_dir + os.path.sep + 'outgoing'
        self.abs_inp_dir = os.getcwd() + os.path.sep + 'incoming'
        self.abs_oup_dir = os.getcwd() + os.path.sep + 'outgoing'
        self.img_queue   = Queue()

    def download_images(self, img_url_list):
        # validate inputs
        if not img_url_list:
            return
        os.makedirs(self.input_dir, exist_ok=True)
        
        logging.info("beginning image downloads")

        start = time.perf_counter()
        os.chdir( self.abs_inp_dir )
        for url in img_url_list:
            # download each image and save to the input dir 
            img_filename = str(url).split(os.path.sep)[-1]
            r            = requests.get( url )
            with open( img_filename, 'wb' ) as f:
               f.write(r.content)
               self.img_queue.put(img_filename)
            
        end = time.perf_counter()
        self.img_queue.put(None)#Poison pill technique, indicate to the consumer that now there is nothing that will be produced on the queue

        logging.info("downloaded {} images in {} seconds".format(len(img_url_list), end - start))

    def perform_resizing(self):
        # validate inputs

        os.makedirs(self.output_dir, exist_ok=True)

        logging.info("beginning image resizing")
        target_sizes = [32, 64, 200]
        num_images = len(os.listdir(self.abs_inp_dir))
        
        start = time.perf_counter()
        while True:
            filename = self.img_queue.get()
            if filename:
                logging.info('Resizing image -- {}'.format(filename))
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
                    
                    img.save( self.abs_oup_dir + os.path.sep + new_filename)

                os.remove(self.abs_inp_dir + os.path.sep + filename)
                logging.info('Done resizing image -- {}'.format(filename))
                self.img_queue.task_done()
            else:
                self.img_queue.task_done() 
                break

        end = time.perf_counter()

        logging.info("created {} thumbnails in {} seconds".format(num_images, end - start))

    def make_thumbnails(self, img_url_list):
        logging.info("START make_thumbnails")
        start = time.perf_counter()

        t1 = Thread(target=self.download_images, args=([img_url_list]))
        t2 = Thread(target=self.perform_resizing)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        end = time.perf_counter()
        logging.info("END make_thumbnails in {} seconds".format(end - start))

    

