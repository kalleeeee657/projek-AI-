import os,unittest
from studio import validate,guard
class Test(unittest.TestCase):
 def setUp(self):
  self.d={'title':'Test','scenes':[{'id':'scene-1','seconds':6,'characters':['STICKMAN_001','AMI_001'],'visual':'Pantai','motion':'Diam','camera':'Wide','narration':'Dinosaurus muncul.'}]}
 def test_valid(self):self.assertEqual(validate(self.d,'Test',6)['totalFrames'],360)
 def test_unknown_character(self):
  self.d['scenes'][0]['characters']=['other']
  with self.assertRaises(ValueError):validate(self.d,'Test',6)
 def test_wrong_duration(self):
  with self.assertRaises(ValueError):validate(self.d,'Test',60)
 def test_guard(self):
  os.environ.pop('CONFIRM_FREE_TIER',None)
  with self.assertRaises(ValueError):guard()
 def test_narration(self):
  self.d['scenes'][0]['narration']='word '*19
  with self.assertRaises(ValueError):validate(self.d,'Test',6)
if __name__=='__main__':unittest.main()
