import asyncio
from ctypes import Structure, c_float, HRESULT, c_int, windll, c_uint32, c_int32, WinError

from rotypes import delegate
from rotypes.idldsl import define_winrt_com_method, generics_cache, define_winrt_com_delegate, pinterface_type
from rotypes.inspectable import IInspectable, IUnknown

_kernel32 = windll.LoadLibrary('kernel32.dll')
_CreateEvent = _kernel32.CreateEventW
_SetEvent = _kernel32.SetEvent
_WaitForSingleObject = _kernel32.WaitForSingleObject
_CloseHandle = _kernel32.CloseHandle


class Rect(Structure):
    _fields_ = (('x', c_float), ('y', c_float), ('width', c_float), ('height', c_float))


class AsyncStatus(c_int32):
    Started = 0
    Completed = 1
    Canceled = 2
    Error = 3


class IAsyncInfo(IInspectable):
    IID = '00000036-0000-0000-C000-000000000046'


@generics_cache
def AsyncOperationCompletedHandler(T):
    cls = pinterface_type('IAsyncOperationCompletedHandler', 'fcdcf02c-e5d8-4478-915a-4d90b74b83a5', (T,),
                          (IUnknown, delegate.delegatebase))
    AsyncOperationCompletedHandler.known_types[(T,)] = cls
    define_winrt_com_delegate(cls, IAsyncOperation(T), AsyncStatus)
    return cls


# IAsyncOperation<IInspectable>
class IAsyncOperation_helpers:
    def as_future(self):
        # FIXME: doesn't work
        future = asyncio.Future()
        if self.Status == AsyncStatus.Completed:
            future.set_result(self.GetResults())
            return future

        def callback(iao, status):
            status = status.value
            if status == AsyncStatus.Completed:
                result = self.GetResults()
                future.set_result(result)
            elif status == AsyncStatus.Error:
                hr = iao.ErrorCode
                future.set_exception(WinError(hr))
            elif status == AsyncStatus.Canceled:
                future.cancel()

        delegatetype = AsyncOperationCompletedHandler(self.__class__._typeparam[0])
        delegateobj = delegatetype.delegate(callback)
        self.Completed = delegateobj
        return future

    def wait(self):
        if self.Status == AsyncStatus.Completed:
            return self.GetResults()
        event = _CreateEvent(None, False, False, None)
        results = []

        def callback(iao, status):
            status = status.value
            if status == AsyncStatus.Completed:
                result = iao.GetResults()
                results.append(result)
                _SetEvent(event)
            elif status == AsyncStatus.Error:
                hr = iao.ErrorCode
                results.append(WinError(hr))
                _SetEvent(event)
            elif status == AsyncStatus.Canceled:
                results.append(RuntimeError('AsyncStatus.Canceled'))

        delegatetype = AsyncOperationCompletedHandler(self.__class__._typeparam[0])
        delegateobj = delegatetype.delegate(callback)
        self.Completed = delegateobj
        # delegateobj._detach()
        _WaitForSingleObject(event, -1)
        _CloseHandle(event)
        result = results[0]
        if isinstance(result, BaseException):
            raise result
        else:
            return result

    def __await__(self):
        return self.as_future().__await__()


@generics_cache
def IAsyncOperation(T):
    cls = pinterface_type('IAsyncOperation', '9fc2b0bb-e446-44e2-aa61-9cab8f636af2', (T,),
                          (IAsyncInfo, IAsyncOperation_helpers))
    IAsyncOperation.known_types[(T,)] = cls
    define_winrt_com_method(cls, 'put_Completed', propput=AsyncOperationCompletedHandler(T), vtbl=6)
    define_winrt_com_method(cls, 'get_Completed', propget=AsyncOperationCompletedHandler(T), vtbl=7)
    define_winrt_com_method(cls, 'GetResults', retval=T, vtbl=8)
    return cls


@generics_cache
def IReference(T):
    cls = pinterface_type('IReference', '61c17706-2d65-11e0-9ae8-d48564015472', (T,), (IInspectable,))
    IAsyncOperation.known_types[(T,)] = cls
    define_winrt_com_method(cls, 'get_Value', propget=T, vtbl=6)
    return cls


class IClosable(IInspectable):
    IID = '30d5a829-7fa4-4026-83bb-d75bae4ea99e'

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Close()


class IStringable(IInspectable):
    IID = '96369f54-8eb6-48f0-abce-c1b211e627c3'

    def __str__(self):
        return str(self.ToString())


define_winrt_com_method(IAsyncInfo, 'get_Id', propget=c_uint32)
define_winrt_com_method(IAsyncInfo, 'get_Status', propget=c_int)
define_winrt_com_method(IAsyncInfo, 'get_ErrorCode', propget=HRESULT)
define_winrt_com_method(IAsyncInfo, 'Cancel')
define_winrt_com_method(IAsyncInfo, 'Close')

define_winrt_com_method(IClosable, 'Close', vtbl=6)

define_winrt_com_method(IStringable, 'ToString', vtbl=6)
