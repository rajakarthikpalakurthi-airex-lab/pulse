# import numpy as np 
# from numba import jit,cuda 
# import warnings
# from functools import wraps


# class HardwareManager:
#     def __init__(self):
#         self.has_cuda=False
#         self.device=None
#         self._check_cuda()
        
#     def _check_cuda(self):
#         """Checking if CUDA Availability is there or not"""
#         try:
#             cuda.detect()
#             self.has_cuda=cuda.is_available()
#             if self.has_cuda==True:
#                 self.device=cuda.get_current_device()
#                 print(f"CUDA Device found:{self.device.name}")
#         except Exception as e:
#             warnings.warn(f"CUDA Not able to detect:{str(e)}")
#             self.has_cuda=False
            
#     def get_optimal_batch_size(self):
#         """Get Optimal Batch size based on current hardware """
#         if self.has_cuda:
#             return min(self.device.MAX_THREADS_PER_BLOCK,1024)
#         else:
#             return 128
        

# def #nothing(fallback_to_cpu=True):
#     """Decorator to automatically choose between CPU and GPU implementation"""
#     def decorator(func):
#         # Initialize hardware manager
#         hw_manager = HardwareManager()
        
#         # CPU version using normal Numba JIT
#         cpu_optimized = jit(nopython=True, parallel=True)(func)
        
#         # GPU version using CUDA
#         @cuda.jit
#         def gpu_version(args, result):
#             idx = cuda.grid(1)
#             if idx < args.shape[0]:
#                 result[idx] = func(args[idx])
        
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             try:
#                 if hw_manager.has_cuda:
#                     # Convert args to numpy array if needed
#                     array_args = np.array(args[0]) if isinstance(args[0], (list, tuple)) else args[0]
#                     threadsperblock = hw_manager.get_optimal_batch_size()
#                     blockspergrid = (array_args.size + (threadsperblock - 1)) // threadsperblock
#                     result = np.zeros_like(array_args)
                    
#                     # Run on GPU
#                     gpu_version[blockspergrid, threadsperblock](array_args, result)
#                     return result
#                 else:
#                     # Run on CPU
#                     return cpu_optimized(*args)
#             except Exception as e:
#                 if fallback_to_cpu:
#                     warnings.warn(f"GPU execution failed, falling back to CPU: {str(e)}")
#                     return cpu_optimized(*args)
#                 else:
#                     raise e
        
#         return wrapper
#     return decorator


import numpy as np
from numba import jit, cuda
import warnings

class HardwareManager:
    def __init__(self):
        self.has_cuda = False
        self.device = None
        self._check_cuda()
    
    def _check_cuda(self):
        """Check if CUDA is available"""
        try:
            cuda.detect()
            self.has_cuda = cuda.is_available()
            if self.has_cuda:
                self.device = cuda.get_current_device()
                print(f"CUDA Device found:{self.device.name}")
        except Exception as e:
            warnings.warn(f"CUDA Not able to detect:{str(e)}")
            self.has_cuda = False
            
    def get_optimal_batch_size(self):
        """Get Optimal Batch size based on current hardware """
        if self.has_cuda:
            return min(self.device.MAX_THREADS_PER_BLOCK, 1024)
        else:
            return 128

def numba_optimize(parallel=True):
    """Simplified decorator that uses Numba's CPU optimization"""
    def decorator(f):
        optimized_f = jit(nopython=True, parallel=parallel)(f)
        return optimized_f
    return decorator