#!/usr/bin/env python3

from hwtest import HWTestBase, StudentTestLoader, StudentRunner

class TestHW(HWTestBase) :

    def setUp(self) :
        pass

    def test_a(self) :
        """ Test a
        
        points=1
        """
        self.assertEqual(self.module.a, 1)
        
    def test_b(self) :
        """ Test b
        
        points=1
        """
        self.assertEqual(self.module.b, 0, msg='{} does not equal 0'.format(self.module.b))
    
    def test_c(self) :
        """ Test c
        
        points=1
        """
        self.assertEqual(len(self.module.c), 2, msg='{} does not equal 2'.format(self.module.b))
    

                     
if __name__ == '__main__' :
    test_class = TestEX
    loader = StudentTestLoader()
    suite = loader.loadTestsFromTestCase(test_class, module=module)
    result = StudentRunner().run(suite, module)       

