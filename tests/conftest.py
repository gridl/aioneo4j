import asyncio

import pytest
from aioneo4j import Neo4j


@pytest.fixture
def loop(request):
    with pytest.raises(RuntimeError):
        asyncio.get_event_loop()

    loop = asyncio.new_event_loop()

    loop.set_debug(True)

    request.addfinalizer(lambda: asyncio.set_event_loop(None))

    yield loop

    loop.call_soon(loop.stop)
    loop.run_forever()
    loop.close()


@pytest.fixture
def neo4j(loop):
    neo4j = Neo4j(loop=loop)
    neo4j.auth = ('neo4j', 'neo4jneo4j')

    yield neo4j

    loop.run_until_complete(neo4j.close())


@pytest.mark.tryfirst
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.funcnamefilter(name):
        item = pytest.Function(name, parent=collector)

        if 'run_loop' in item.keywords:
            return list(collector._genfunctions(name, obj))


@pytest.mark.tryfirst
def pytest_pyfunc_call(pyfuncitem):
    if 'run_loop' in pyfuncitem.keywords:
        funcargs = pyfuncitem.funcargs

        loop = funcargs['loop']

        testargs = {
            arg: funcargs[arg]
            for arg in pyfuncitem._fixtureinfo.argnames
        }

        assert asyncio.iscoroutinefunction(pyfuncitem.obj)

        loop.run_until_complete(pyfuncitem.obj(**testargs))

        return True
