# this module contains the http request mechanism

from pydantic import validate_call, Field
import aiohttp.web_exceptions as excepts
from typing_extensions import Annotated
import urllib.request
import aiohttp
import os.path
import ssl


# prepare LindenLab.crt
__llcacrt = "LindenLab.crt"
__sslcontext = None
if not __sslcontext:
    if not os.path.isfile("LindenLab.crt"):
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/secondlife/llca/master/LindenLab.crt",
            __llcacrt,
        )
    __sslcontext = ssl.create_default_context(cafile=__llcacrt)
    __sslcontext.set_ciphers("ALL:@SECLEVEL=1")


# select exception type by responce.staus
@validate_call
def __exceptionByResp(
    resp=Annotated[aiohttp.ClientResponse, Field()],
) -> excepts.HTTPException:
    code = resp.status
    if resp.reason:
        reason = resp.reason
    else:
        reason = None
    err: Exception = excepts.HTTPError(reason=reason, headers=resp.headers)
    match code:
        case 200:
            err = excepts.HTTPOk(reason=reason, headers=resp.headers)
        case 201:
            err = excepts.HTTPCreated(reason=reason, headers=resp.headers)
        case 202:
            err = excepts.HTTPAccepted(reason=reason, headers=resp.headers)
        case 203:
            err = excepts.HTTPNonAuthoritativeInformation(
                reason=reason, headers=resp.headers
            )
        case 204:
            err = excepts.HTTPNoContent(reason=reason, headers=resp.headers)
        case 205:
            err = excepts.HTTPResetContent(reason=reason, headers=resp.headers)
        case 206:
            err = excepts.HTTPPartialContent(reason=reason, headers=resp.headers)

        case 300:
            err = excepts.HTTPMultipleChoices(
                reason=reason, headers=resp.headers, location=resp.headers["Location"]
            )
        case 301:
            err = excepts.HTTPMovedPermanently(
                reason=reason, headers=resp.headers, location=resp.headers["Location"]
            )
        case 302:
            err = excepts.HTTPFound(
                reason=reason, headers=resp.headers, location=resp.headers["Location"]
            )
        case 303:
            err = excepts.HTTPSeeOther(
                reason=reason, headers=resp.headers, location=resp.headers["Location"]
            )
        case 304:
            err = excepts.HTTPNotModified(reason=reason, headers=resp.headers)
        case 305:
            err = excepts.HTTPUseProxy(
                reason=reason, headers=resp.headers, location=resp.headers["Location"]
            )
        case 307:
            err = excepts.HTTPTemporaryRedirect(
                reason=reason, headers=resp.headers, location=resp.headers["Location"]
            )
        case 308:
            err = excepts.HTTPPermanentRedirect(
                reason=reason, headers=resp.headers, location=resp.headers["Location"]
            )

        case 400:
            err = excepts.HTTPBadRequest(reason=reason, headers=resp.headers)
        case 401:
            err = excepts.HTTPUnauthorized(reason=reason, headers=resp.headers)
        case 402:
            err = excepts.HTTPPaymentRequired(reason=reason, headers=resp.headers)
        case 403:
            err = excepts.HTTPForbidden(reason=reason, headers=resp.headers)
        case 404:
            err = excepts.HTTPNotFound(reason=reason, headers=resp.headers)
        case 405:
            err = excepts.HTTPMethodNotAllowed(
                reason=reason,
                headers=resp.headers,
                method=resp.method,
                allowed_methods=resp.headers["Allow"].split(),
            )
        case 406:
            err = excepts.HTTPNotAcceptable(reason=reason, headers=resp.headers)
        case 407:
            err = excepts.HTTPProxyAuthenticationRequired(
                reason=reason, headers=resp.headers
            )
        case 408:
            err = excepts.HTTPRequestTimeout(reason=reason, headers=resp.headers)
        case 409:
            err = excepts.HTTPConflict(reason=reason, headers=resp.headers)
        case 410:
            err = excepts.HTTPGone(reason=reason, headers=resp.headers)
        case 411:
            err = excepts.HTTPLengthRequired(reason=reason, headers=resp.headers)
        case 412:
            err = excepts.HTTPPreconditionFailed(reason=reason, headers=resp.headers)
        case 413:
            err = excepts.HTTPRequestEntityTooLarge(
                reason=reason,
                headers=resp.headers,
                max_size=0,
                actual_size=resp.headers["Content-Length"],
            )
        case 414:
            err = excepts.HTTPRequestURITooLong(reason=reason, headers=resp.headers)
        case 415:
            err = excepts.HTTPUnsupportedMediaType(reason=reason, headers=resp.headers)
        case 416:
            err = excepts.HTTPRequestRangeNotSatisfiable(
                reason=reason, headers=resp.headers
            )
        case 417:
            err = excepts.HTTPExpectationFailed(reason=reason, headers=resp.headers)
        case 421:
            err = excepts.HTTPMisdirectedRequest(reason=reason, headers=resp.headers)
        case 422:
            err = excepts.HTTPUnprocessableEntity(reason=reason, headers=resp.headers)
        case 424:
            err = excepts.HTTPFailedDependency(reason=reason, headers=resp.headers)
        case 426:
            err = excepts.HTTPUpgradeRequired(reason=reason, headers=resp.headers)
        case 429:
            err = excepts.HTTPTooManyRequests(reason=reason, headers=resp.headers)
        case 431:
            err = excepts.HTTPRequestHeaderFieldsTooLarge(
                reason=reason, headers=resp.headers
            )
        case 451:
            err = excepts.HTTPUnavailableForLegalReasons(
                reason=reason, headers=resp.headers, link=None
            )

        case 500:
            err = excepts.HTTPInternalServerError(reason=reason, headers=resp.headers)
        case 501:
            err = excepts.HTTPNotImplemented(reason=reason, headers=resp.headers)
        case 502:
            err = excepts.HTTPBadGateway(reason=reason, headers=resp.headers)
        case 503:
            err = excepts.HTTPServiceUnavailable(reason=reason, headers=resp.headers)
        case 504:
            err = excepts.HTTPGatewayTimeout(reason=reason, headers=resp.headers)
        case 505:
            err = excepts.HTTPVersionNotSupported(reason=reason, headers=resp.headers)
        case 506:
            err = excepts.HTTPVariantAlsoNegotiates(reason=reason, headers=resp.headers)
        case 507:
            err = excepts.HTTPInsufficientStorage(reason=reason, headers=resp.headers)
        case 510:
            err = excepts.HTTPNotExtended(reason=reason, headers=resp.headers)
        case 511:
            err = excepts.HTTPNetworkAuthenticationRequired(
                reason=reason, headers=resp.headers
            )

        case code if code < 300:
            err = excepts.HTTPSuccessful(reason=reason, headers=resp.headers)
        case code if code < 400:
            err = excepts.HTTPRedirection(reason=reason, headers=resp.headers)
        case code if code < 500:
            err = excepts.HTTPClientError(reason=reason, headers=resp.headers)
        case _:
            err = excepts.HTTPServerError(reason=reason, headers=resp.headers)

    return err


# http get method
async def get(url: str) -> aiohttp.ClientResponse:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=__sslcontext) as resp:
            await resp.text()
            if resp.status not in range(200, 203):
                raise __exceptionByResp(resp)
            return resp
