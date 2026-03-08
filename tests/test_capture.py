import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import sys
sys.path.insert(0, '/Users/adolf/Desktop/kanjilens/src')

from capture.screen import capture_full, capture_region

class TestCapture(unittest.TestCase):
    @patch('capture.screen.mss')
    def test_capture_full(self, mock_mss):
        """Test full screen capture"""
        mock_screen = MagicMock()
        mock_screen.__enter__ = MagicMock(return_value=mock_screen)
        mock_screen.__exit__ = MagicMock(return_value=False)
        mock_screenshot = np.zeros((1080, 1920, 3), dtype=np.uint8)
        mock_screen.grab.return_value = mock_screenshot
        
        mock_mss.return_value = mock_screen
        
        result = capture_full()
        
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (1080, 1920, 3))
    
    @patch('capture.screen.mss')
    def test_capture_region(self, mock_mss):
        """Test region capture"""
        region = (0, 0, 800, 600)
        
        mock_screen = MagicMock()
        mock_screen.__enter__ = MagicMock(return_value=mock_screen)
        mock_screen.__exit__ = MagicMock(return_value=False)
        mock_screenshot = np.zeros((600, 800, 3), dtype=np.uint8)
        mock_screen.grab.return_value = mock_screenshot
        
        mock_mss.return_value = mock_screen
        
        result = capture_region(region)
        
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (600, 800, 3))

if __name__ == '__main__':
    unittest.main()