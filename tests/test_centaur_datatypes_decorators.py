from centaur.datatypes import ValidationError, validate_args, def_datatypes, load_module
from centaur.utils import select_items
import pytest


url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'


def test_validate_args_w_datatypes_as_strings():
    ctx = def_datatypes({
        "url": {"type": "string", "regex": url_regex},
        "positive": {"type": "number", "gt": 0},
    })

    @validate_args(ctx=ctx, pkw={'type': 'string', 'length_min': 1})
    def _test_fn(url: "url", no_annotation, pkw, param_w_default: 'positive'=None):
        return "valid url:{0}".format(url)

    assert _test_fn("http://example.com", None, 'A', None) == "valid url:http://example.com"
    with pytest.raises(ValidationError):
        _test_fn("s,djkdjfkdjsdkjfksdjf", None, '')
    with pytest.raises(ValidationError):
        _test_fn("http://example.com", None,  '1', param_w_default=-1)


def test_validate_args_w_datatypes_as_dt():
    ctx = def_datatypes(
        {
            "url": {"type": "string", "regex": url_regex},
            "positive": {"type": "number", "gt": 0},
        })

    url_dt, positive_dt = select_items(ctx, ["url", "positive"])

    @validate_args
    def _test_fn(url: url_dt, no_annotation,  param_w_default: positive_dt=None):
        return "valid url:{0}".format(url)

    assert _test_fn("http://example.com", None) == "valid url:http://example.com"
    with pytest.raises(ValidationError):
        _test_fn("s,djkdjfkdjsdkjfksdjf", None)
    with pytest.raises(ValidationError):
        _test_fn("http://example.com", None,  param_w_default=-1)


def test_validate_args_w_bad_datatype_name():
    @validate_args
    def _test_fn(email: "email2"):
        return "valid email:{0}".format(email)

    with pytest.raises(KeyError):
        _test_fn("goodemail@example.com")


def test_validate_args_w_default_ctx():
    param_def = {
        "type": "string",
        "length_min": 1}

    @validate_args
    def _test_fn(param: param_def):
        return param

    for p in [1, "", 0.1]:
        with pytest.raises(ValidationError):
            _test_fn(1)

    assert _test_fn("a") == "a"


def test_validate_args_w_params_decorator():
    param_def = {
        "type": "string",
        "length_min": 1}

    @validate_args(param=param_def)
    def _test_fn(param):
        return param

    for p in [1, "", 0.1]:
        with pytest.raises(ValidationError):
            _test_fn(1)

    assert _test_fn("a") == "a"


def test_validate_args_w_module():
    module_def = {
        'datatypes': {
            'sample': {
                'type': 'string',
                'length_min': 1
            }
        }}

    module_ = load_module(module_def)

    @validate_args(ctx=module_)
    def _test_fn(param: 'sample'):
        return param

    for p in [1, "", 0.1]:
        with pytest.raises(ValidationError):
            _test_fn(1)

    assert _test_fn("a") == "a"
