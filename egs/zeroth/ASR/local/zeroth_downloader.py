import boto3
import threading
import sys


class ProgressPercentage(object):
    ''' Progress Class
    Class for calculating and displaying download progress
    '''
    # https://gist.github.com/egeulgen/538aadc90275d79d514a5bacc4d5694e

    def __init__(self, client, bucket, filename):
        ''' Initialize
        initialize with: file name, file size and lock.
        Set seen_so_far to 0. Set progress bar length
        '''
        self._filename = filename
        self._size = client.head_object(Bucket=bucket, Key=filename)[
            'ContentLength']
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self.prog_bar_len = 80

    def __call__(self, bytes_amount):
        ''' Call
        When called, increments seen_so_far by bytes_amount,
        calculates percentage of seen_so_far/total file size
        and prints progress bar.
        '''
        # To simplify we'll assume this is hooked up to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            ratio = round((float(self._seen_so_far) /
                          float(self._size)) * (self.prog_bar_len - 6), 1)
            current_length = int(round(ratio))

            percentage = round(100 * ratio / (self.prog_bar_len - 6), 1)

            bars = '+' * current_length
            output = bars + ' ' * (self.prog_bar_len - current_length -
                                   len(str(percentage)) - 1) + str(percentage) + '%'

            if self._seen_so_far != self._size:
                sys.stdout.write(output + '\r')
            else:
                sys.stdout.write(output + '\n')
            sys.stdout.flush()


class ZerothSpeechDownloader():
    """ZerothSpeechDownloader
    Class for downloading files from AWS
    """

    def __init__(self,
                 aws_access_key_id="AKIASLNRD65N3ETEFPJW",
                 aws_secret_access_key="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",
                 region_name="ap-northeast-2"):

        self.client = boto3.client('s3',
                                   aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key,
                                   region_name=region_name)
        self.bucket_name = 'zeroth-opensource'

    def download(self, filename, dest_name):
        s3 = boto3.resource('s3')
        progress = ProgressPercentage(self.client, self.bucket_name, filename)
        s3.Bucket(self.bucket_name).download_file(
            filename, dest_name, Callback=progress)
