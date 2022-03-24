# Credit to Ulrich Stern on Stack Overflow
# https://stackoverflow.com/questions/45310718/opencv-python-how-to-get-latest-frame-from-the-live-video-stream-or-skip-old-on?noredirect=1&lq=1

import cv2, queue, threading

# bufferless VideoCapture
class BufferlessVideoCapture:
  def __init__(self, cam_index, image_width, image_height, fps):
    self.cap = cv2.VideoCapture(cam_index)
    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, image_width)
    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, image_height)
    self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    self.cap.set(cv2.CAP_PROP_FPS, fps)

    self.q = queue.Queue()
    t = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()

  # read frames as soon as they are available, keeping only most recent one
  def _reader(self):
    while True:
      ret, frame = self.cap.read()
      if not ret:
        break
      if not self.q.empty():
        try:
          self.q.get_nowait() # discard previous (unprocessed) frame
        except queue.Empty:
          pass
      self.q.put(frame)

  def read(self):
    return self.q.get()