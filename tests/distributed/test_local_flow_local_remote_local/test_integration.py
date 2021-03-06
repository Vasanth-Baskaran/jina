import os

import pytest

from jina import Document
from jina.flow import Flow

cur_dir = os.path.dirname(os.path.abspath(__file__))
compose_yml = os.path.join(cur_dir, 'docker-compose.yml')
flow_yml = os.path.join(cur_dir, 'flow.yml')


@pytest.mark.skip('Conflict with https://github.com/jina-ai/jina/pull/1697, '
                  'the latter aims to solve the dameon on aws can not transfer data to local laptop behind a router. '
                  'Feel like the dockercompose environment is not a perfect simulation of the real-world case.')
@pytest.mark.parametrize('docker_compose', [compose_yml], indirect=['docker_compose'])
@pytest.mark.parametrize('encoder_needs, indexer_needs', [('crafter', 'encoder'), ('gateway', '[encoder, crafter]')])
def test_flow(docker_compose, tmpdir, mocker, encoder_needs, indexer_needs):
    text = 'cats rules'
    m = mocker.Mock()

    def validate_output(resp):
        m()
        assert len(resp.index.docs) == 1
        assert resp.index.docs[0].text == text

    os.environ['JINA_ENCODER_HOST'] = '172.28.1.1'
    os.environ['JINA_WORKSPACE'] = str(tmpdir)
    os.environ['JINA_ENCODER_NEEDS'] = encoder_needs
    os.environ['JINA_INDEXER_NEEDS'] = indexer_needs

    with Document() as doc:
        doc.content = text

    with Flow.load_config(flow_yml) as f:
        f.index([doc], on_done=validate_output)

    m.assert_called_once()
