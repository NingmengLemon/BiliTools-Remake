from typing import Optional

from requests import Session, adapters

from biliapis.wbi import CachedWbiManager

# collect components
from . import apis

components = [v for k, v in vars(apis).items() if k.endswith("APIs")]


class APIContainer:
    pass


def default_session():
    # 加一些，默认的优化选项，像 Retry Adapter？
    session = Session()
    retry = adapters.Retry(total=2, backoff_factor=0.5, backoff_max=10)
    adp = adapters.HTTPAdapter(max_retries=retry)
    session.mount("https://", adp)
    session.mount("http://", adp)
    return session


def new_apis(
    session: Optional[Session] = None, wbimanager: Optional[CachedWbiManager] = None
) -> APIContainer:
    session = session if session else default_session()
    wbimanager = wbimanager if wbimanager else CachedWbiManager()

    container = APIContainer()
    for compcls in components:
        setattr(
            container,
            compcls.__name__.removesuffix("APIs").lower(),
            compcls(session=session, wbimanager=wbimanager),
        )
    return container
