## FormEncode, a  Form processor
## Copyright (C) 2003, Ian Bicking <ianb@colorstudy.com>
##
## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public
## License as published by the Free Software Foundation; either
## version 2.1 of the License, or (at your option) any later version.
##
## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public
## License along with this library; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
##
## NOTE: In the context of the Python environment, I interpret "dynamic
## linking" as importing -- thus the LGPL applies to the contents of
## the modules, but make no requirements on code importing these
## modules.
"""
Validator/Converters for use with FormEncode.
"""

try:
    from MiscUtils import NoDefault
except ImportError:
    class NoDefault:
        pass
import re, string, socket
import cgi
htmlEncode = cgi.escape
DateTime = None
mxlookup = None

True, False = (1==1), (0==1)

class InvalidField(Exception):

    def __init__(self, msg, value, state, errorList=None, errorDict=None):
        self.msg = msg
        self.value = value
        self.state = state
        self.errorList = errorList
        self.errorDict = errorDict

    def __str__(self):
        val = str(self.msg)
        if self.value:
            val += ".  Value: %s" % repr(self.value)
        return val

def toPython(obj, value, state):
    return _validateToSomething(obj, value, state,
                               lambda v: v.toPython)

def fromPython(obj, value, state):
    return _validateToSomething(obj, value, state,
                               lambda v: v.fromPython)

def getValidator(obj):
    if isinstance(obj, type):
        obj = obj()
    if not isinstance(obj, Validator):
        if hasattr(obj, 'validator'):
            obj = obj.validator
        else:
            return None
    if isinstance(obj, list):
        obj = All(*obj)
    return obj

def _validateToSomething(obj, value, state, finisher):
    validator = getValidator(obj)
    if validator is None:
        return value
    try:
        prot = state.protocol
    except AttributeError:
        pass
    else:
        if validator.protocols is not None \
           and prot is not None \
           and prot not in validator.protocols:
            return value
    return finisher(validator)(value, state)

class Validator(object):

    repeating = False
    messages = None
    input = None
    protocols = None
    ifMissing = NoDefault

    def __init__(self, **kw):
        for name, value in kw.items():
            setattr(self, name, value)

    def __call__(self, **kw):
        if not kw:
            return self
        d = self.__dict__.copy()
        d.update(kw)
        return self.__class__(**d)

    def toPython(self, value, state=None):
        return value

    def fromPython(self, value, state=None):
        return value

    def message(self, name, default):
        if not self.messages:
            return default
        return self.messages.get(name, default)


class FancyValidator(Validator):
    """
    Validator is the (abstract) superclass for various
    validators and converters.  A subclass can validate, convert, or
    do both.  There is no formal distinction made here.

    Validators have two important external methods:
    * .toPython(value, state):
      Attempts to convert the value.  If there is a problem, or the
      value is not valid, an InvalidField exception is raised.  The
      argument for this exception is the (potentially HTML-formatted)
      error message to give the user.
    * .fromPython(value, state):
      Reverses toPython.

    There are three important methods for subclasses to override:
    * __init__(), of course.
    * .validatePython(value, state):
      This should raise an error if necessary.  The value is a Python
      object, either the result of toPython, or the input to
      fromPython.
    * .validateOther(value, state):
      Validates the source, before toPython, or after fromPython.
    * ._toPython(value, state):
      This returns the converted value, or raises an InvalidField
      exception if there is an error.  The argument to this exception
      should be the error message.
    * ._fromPython(value, state):
      Should undo .toPython() in some reasonable way, returning
      a string.
    * .sqlToPython(value, state):
    * .pythonToSQL(value, state):

    Validators should have no internal state besides the
    values given at instantiation.  They should be reusable and
    reentrant.
    """

    ifInvalid = NoDefault
    ifEmpty = NoDefault
    notEmpty = False
    htmlView = None

    def __init__(self, **kw):
        if kw.has_key('htmlView'):
            if isinstance(kw['htmlView'], type):
                kw['htmlView'] = kw['htmlView']()
            kw['htmlView'].owner = self
        Validator.__init__(self, **kw)

    def attemptConvert(self, value, state, pre, convert, post):
        if not value:
            if self.ifEmpty is not NoDefault:
                return self.ifEmpty
            if self.notEmpty:
                raise InvalidField(self.message('empty', "Please enter a value"), value, state)
        try:
            if pre:
                pre(value, state)
            if convert:
                converted = convert(value, state)
            else:
                converted = value
            if post:
                post(value, state)
            return converted
        except InvalidField:
            if self.ifInvalid is NoDefault:
                raise
            else:
                return self.ifInvalid

    def toPython(self, value, state=None):
        return self.attemptConvert(value, state,
                                   self.validateOther,
                                   self._toPython,
                                   self.validatePython)

    def fromPython(self, value, state):
        return self.attemptConvert(value, state,
                                   self.validatePython,
                                   self._fromPython,
                                   self.validateOther)

    validatePython = None
    validateOther = None
    _toPython = None
    _fromPython = None

    def javascript(self, state, form_name, field_name, field_description):
        """By default there is no JavaScript validation"""
        return ""

class CompoundValidator(FancyValidator):

    def __init__(self, *validators, **kw):
        if kw.has_key('ifInvalid'):
            ifInvalid = kw['ifInvalid']
            del kw['ifInvalid']
        else:
            ifInvalid = NoDefault
        assert not kw, '%s only takes the ifInvalid keyword argument' % self.__class__.__name__
        if not validators:
            raise TypeError, 'You must pass at least one validator to %s' % self.__class__.__name__
        self.validators = validators
        FancyValidator.__init__(self, ifInvalid=ifInvalid, **kw)

    def _toPython(self, value, state=None):
        return self.attemptConvert(self, value, state,
                                   toPython)

    def _fromPython(self, value, state):
        return self.attemptConvert(self, value, state,
                                   fromPython)

    def matchesProtocol(self, validator, state):
        target = validator.protocols
        prot = getattr(state, 'protocol')
        if target is None or prot is None:
            return True
        return prot in target

class Any(CompoundValidator):
    """This class is like an 'or' operator for validators.
    The first validator/converter that validates the value will
    be used.  (You can pass in lists of validators, which will
    be anded)
    """

    def attemptConvert(self, value, state, validate):
        lastException = None
        for validator in self.validators:
            if not self.matchesProtocol(validator, state):
                continue
            try:
                return validate(validator, value, state)
            except InvalidField, e:
                lastException = e
        if self.ifInvalid is NoDefault:
            raise e
        else:
            return self.ifInvalid

class All(CompoundValidator):

    def attemptConvert(self, value, state, validate):
        for validator in self.validators:
            if not self.matchesProtocol(validator, state):
                continue
            value = validate(validator, value, state)
        return value

    def withValidator(self, validator):
        new = self.validators[:]
        if isinstance(validator, list) or isinstance(validator, tuple):
            new.extend(validator)
        else:
            new.append(validator)
        return self.__class__(*new)

    def join(cls, first, *validators):
        if isinstance(first, All):
            return first.withValidator(validators)
        else:
            # Get rid of any None values in the list:
            validators = filter(None, validators)
            if not validators:
                return first
            return cls(first, *validators)
    join = classmethod(join)

class ForEach(CompoundValidator):
    """
    Use this to apply a validator/converter to each item in a list.
    For instance:
      ValidateList(AsInt(), InList([1, 2, 3]))
    Will take a list of values and try to convert each of them to
    an integer, and then check if each integer is 1, 2, or 3.
    """

    def attemptConvert(self, value, state, validate):
        newList = []
        errors = []
        allGood = True
        for subValue in value:
            goodPass = True
            for validator in self.validators:
                if not self.matchesProtocol(validator, state):
                    continue
                try:
                    subValue = validate(validator, subValue, state)
                except InvalidField, e:
                    errors.append(e)
                    allGood = False
                    goodPass = False
                    break
            if goodPass:
                errors.append(None)
            newList.append(subValue)
        if allGood:
            return newList
        else:
            raise InvalidField(
                'Errors:\n%s' % '\n'.join([str(e) for e in errors if e]),
                value,
                state,
                errorList = errors)

class ConfirmType(FancyValidator):

    def __init__(self, subclass=None, type=None, **kw):
        if subclass:
            self.subclass = subclass
            self.toPython = self.confirmSubclass
            self.fromPython = self.confirmSubclass
        if type:
            if isinstance(type, ()):
                self.inType = type
                self.toPython = self.confirmInType
                self.fromPython = self.confirmInType
            else:
                self.type = type
                self.toPython = self.confirmType
                self.fromPython = self.confirmType

    def confirmSubclass(self, value, state):
        if not isinstance(value, self.subclass):
            raise InvalidField(self.message('subclass', "%(object)s is not a subclass of %(subclass)s")
                               % {'object': repr(value),
                                  'subclass': self.subclass},
                               value, state)
        return value

    def confirmInType(self, value, state):
        if not type(value) in self.inType:
            raise InvalidField(self.message('inType', "%(object)s must be one of the types %(typeList)s")
                               % {'object': repr(value),
                                  'typeList': ', '.join(map(repr, self.inType))},
                               value, state)
        return value

    def confirmType(self, value, state):
        if not type(value) is self.type:
            raise InvalidField(self.message('type', "%(object)s must be of the type %(type)s")
                               % {'object': repr(value),
                                  'type': self.type},
                               value, state)
        return value

class Wrapper(FancyValidator):

    def __init__(self, toPython=None, fromPython=None,
                 validatePython=None, validateOther=None, **kw):
        self._toPython = self.wrap(toPython)
        self._fromPython = self.wrap(fromPython)
        self.validatePython = self.wrap(validatePython)
        self.validateOther = self.wrap(validateOther)
        FancyValidator.__init__(self, **kw)

    def wrap(self, func):
        if not func: return None
        def result(value, state, func=func):
            try:
                return func(value)
            except Exception, e:
                raise InvalidField(str(e), value, state)
        return result

class Constant(FancyValidator):
    """This converter converts everything to the same thing.  I.e., you
    pass in the constant value when initializing, then all values get
    converted to that constant value.

    This is only useful with ValidateAny, as in:
      fromEmailValidator = ValidateAny(ValidEmailAddress(), Constant("unknown@localhost"))
    In this case, the if the email is not valid "unknown@localhost" will be
    used instead.
    """

    def __init__(self, value, **kw):
        self.value = value
        FancyValidator.__init__(self, **kw)

    def _toPython(self, value, state):
        return self.value

    _fromPython = _toPython

class MaxLength(FancyValidator):

    def __init__(self, maxLength, **kw):
        self.maxLength = maxLength
        FancyValidator.__init__(self, **kw)

    def validatePython(self, value, state):
        try:
            if value and \
               len(value) > self.maxLength:
                raise InvalidField(self.message('tooLong', "Enter a value less than %(maxLength)i characters long") % {"maxLength": self.maxLength}, value, state)
            else:
                return None
        except TypeError:
            raise InvalidField(self.message('invalid', "Invalid value"), value, state)

class MinLength(FancyValidator):

    def __init__(self, minLength, **kw):
        self.minLength = minLength
        FancyValidator.__init__(self, **kw)

    def validatePython(self, value, state):
        if len(value) < self.minLength:
            raise InvalidField(self.message('tooShort', "Enter a value more than %(minLength)i characters long") % {"minLength": self.minLength}, value, state)

class NotEmpty(FancyValidator):

    def validatePython(self, value, state):
        if not value:
            raise InvalidField(self.message('empty', "Please enter a value"), value, state)

class Empty(FancyValidator):
    """Useful with ValidateAny"""

    def validatePython(self, value, state):
        if value:
            raise InvalidField(self.message('notEmpty', "You cannot enter a value here"), value, state)

class Regex(FancyValidator):

    def __init__(self, regex, strip=False, **kw):
        if isinstance(regex, str):
            regex = re.compile(regex)
        self.regex = regex
        self.strip = strip
        FancyValidator.__init__(self, **kw)

    def validatePython(self, value, state):
        if self.strip and (isinstance(value, str) or isinstance(value, unicode)):
            value = value.strip()
        if not self.regex.search(value):
            raise InvalidField(self.message('invalid', "The input is not valid"), value, state)

    def _toPython(self, value, state):
        if self.strip and \
               (isinstance(value, str) or isinstance(value, unicode)):
            return value.strip()
        return value

class PlainText(Regex):

    def __init__(self, **kw):
        if not kw.setdefault('messages', {}).has_key('invalid'):
            kw['messages']['invalid'] = 'Enter only letters, numbers, or _ (underscore)'
            Regex.__init__(self, r"^[a-zA-Z_\-0-9]*$", **kw)

class OneOf(FancyValidator):

    def __init__(self, l, allowSublists=False, hideList = False,
                 **kw):
        """if hideList is true then the list will not be displayed in
        error messages"""
        self.list = l
        self.hideList = hideList
        self.allowSublists = allowSublists
        FancyValidator.__init__(self, **kw)

    def validatePython(self, value, state):
        if self.allowSublists and (type(value) is type([]) \
                              or type(value) is type(())):
            results = filter(None, [self.validate(v, state) for v in value])
            if results:
                raise InvalidField(string.join(results, '<br>\n'),
                                   value, state, errorList=results)
        if not value in self.list:
            if self.hideList:
                raise InvalidField(self.message('invalid', "Invalid value"),
                                   value, state)
            else:
                raise InvalidField(self.message('notIn', "Value must be one of: %(items)s") % {"items": htmlEncode(string.join(self.list, "; "))}, value, state)

class DictionaryConverter(FancyValidator):
    """Converts values based on a dictionary which has preprocessed
    values as keys for the resultant values.  If allowNull is passed,
    it will not balk if a false value (e.g., "" or None) is given (it
    will return None in these cases).  """

    def __init__(self, dict, **kw):
        self.dict = dict
        FancyValidator.__init__(self, **kw)

    def _toPython(self, value, state):
        if not self.dict.has_key(value):
            raise InvalidField(self.message('invalid', "Choose something"),
                               value, state)
        else:
            return self.dict[value]

    def _fromPython(self, value, state):
        for k, v in self.dict.items():
            if value == v:
                return k
        raise InvalidField("Nothing in my dictionary goes by the value %s"
                           % repr(value), value, state)

class IndexListConverter(FancyValidator):
    """Converts a index (which may be a string like "2") to the value
    in the given list."""

    def __init__(self, l, **kw):
        self.list = l
        FancyValidator.__init__(self, **kw)

    def _toPython(self, value, state):
        try:
            value = int(value)
        except ValueError:
            raise InvalidField(self.message('integer', "Must be an integer index"), value, state)
        try:
            return self.list[value]
        except IndexError:
            raise InvalidField(self.message('outOfRange', "Index out of range"), value, state)

    def _fromPython(self, value, state):
        for i in range(len(self._list)):
            if self.list[i] == value:
                return i
        raise InvalidField("Item %s was not found in the list"
                           % repr(value), value, state)

class DateValidator(FancyValidator):
    """Be sure to call DateConverter first"""

    def __init__(self, earliestDate=None, latestDate=None, **kw):
        self.earliestDate = earliestDate
        self.latestDate = latestDate
        FancyValidator.__init__(self, **kw)

    def validatePython(self, value, state):
        if self.earliestDate and value < self.earliestDate:
            raise InvalidField(
                self.message('after', "Date must be after %(date)s") % \
                {"date": self.earliestDate.strftime(self.message('dateFormat', "%A, %d %B %Y"))},
                value, state)
        if self.latestDate and value > self.latestDate:
            raise InvalidField(
                self.message('before', "Date must be before %(date)s") % \
                {"date": self.latestDate.strftime(self.message('dateFormat', "%A, %d %B %Y"))},
                value, state)

class Int(FancyValidator):

    def _toPython(self, value, state):
        try:
            return int(value)
        except ValueError:
            raise InvalidField(self.message('integer', "Please enter an integer value"), value, state)

class Number(FancyValidator):

    def _toPython(self, value, state):
        try:
            value = float(value)
            if value == int(value):
                return int(value)
            return value
        except ValueError:
            raise InvalidField(self.message('number', "Please enter a number"), value, state)

class String(FancyValidator):
    """
    Converts things to string, but treats empty things as the empty
    string.
    """

    def __init__(self, max=None, min=None, **kw):
        self.max = max
        self.min = min
        FancyValidator.__init__(self, **kw)

    def validatePython(self, value, state):
        if self.max is not None and len(value) > self.max:
            raise InvalidField(self.message('tooLong', "Enter a value less than %(max)i characters long") % {"max": self.max}, value, state)
        if self.min is not None and len(value) < self.min:
            raise InvalidField(self.message('tooShort', "Enter a value %(min)i characters long or more") % {"min": self.min}, value, state)

    def _fromPython(self, value, state):
        if value: return str(value)
        if value == 0: return str(value)
        return ""

class Set(FancyValidator):
    """This is for when you think you may return multiple values
    for a certain field.  This way the result will always be a
    list, even if there's only one result.

    @@ 2001-04-11 ib: Maybe this should deal with no result ([])
    Maybe I'm not sure it works at all.
    """

    def _toPython(self, value, state):
        if not type(value) is type([]):
            return [value]
        else:
            return value

class Email(FancyValidator):
    """Validate an email address.  If you pass resolveDomain=True,
    then it will try to resolve the domain name to make sure it's valid.
    This takes longer, of course.  You must have the pyDNS modules
    installed <http://pydns.sf.net> to look up MX records.
    """

    usernameRE = re.compile(r"^[a-z0-9\_\-']+", re.I)
    domainRE = re.compile(r"^[a-z0-9\.\-]+\.[a-z]+$", re.I)

    def __init__(self, resolveDomain=False, **kw):
        global mxlookup
        if resolveDomain:
            if mxlookup is None:
                try:
                    from DNS.lazy import mxlookup
                except ImportError:
                    import warnings
                    warnings.warn("pyDNS <http://pydns.sf.net> is not installed on your system (or the DNS package cannot be found).  I cannot resolve domain names in addresses")
                    raise
        self.resolveDomain = resolveDomain
        FancyValidator.__init__(self, **kw)

    def validatePython(self, value, state):
        if not value:
            raise InvalidField(
                self.message('empty', 'Please enter an email address'),
                value, state)
        value = string.strip(value)
        splitted = string.split(value, '@', 1)
        if not len(splitted) == 2:
            raise InvalidField(
                self.message('noAt', 'An email address must contain an @'),
                value, state)
        if not self.usernameRE.search(splitted[0]):
            raise InvalidField(
                self.message('badUsername', 'The username portion of the email address is invalid (the portion before the @: %(username)s)') % {"username": htmlEncode(splitted[0])},
                value, state)
        if not self.domainRE.search(splitted[1]):
            raise InvalidField(
                self.message('badDomain', 'The domain portion of the email address is invalid (the portion after the @: %(domain)s)') % {"domain": htmlEncode(splitted[1])},
                value, state)
        if self.resolveDomain:
            domains = mxlookup(splitted[1])
            if not domains:
                raise InvalidField(
                    self.message('domainDoesNotExist', 'The domain of the email address does not exist (the portion after the @: %(domain)s)') % {"domain": splitted[1]},
                    value, state)

    def _toPython(self, value, state):
        return string.strip(value)

class StateProvince(FancyValidator):
    """
    Valid state or province code (two-letter).  Well, for now I don't
    know the province codes, but it does state code.
    """

    states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE',
               'FL', 'GA', 'HI', 'IA', 'ID', 'IN', 'IL', 'KS', 'KY',
               'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT',
               'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH',
               'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT',
               'VA', 'VT', 'WA', 'WI', 'WV', 'WY']

    def __init__(self, extraStates=None, **kw):
        """
        extraStates are other postal codes allowed, like provinces
        or whatnot.  If you want an entirely different set of codes,
        then you should just subclass this and change _states
        """
        FancyValidator.__init__(self, **kw)
        self.extraStates = extraStates

    def validatePython(self, value, state):
        value = string.strip(string.upper(value))
        if not value:
            raise InvalidField(
                self.message('empty', 'Please enter a state code'),
                value, state)
        if len(value) != 2:
            raise InvalidField(
                self.message('wrongLength', 'Please enter a state code with TWO letters'),
                value, state)
        if value not in self.states \
           and not (self.extraStates and value in self.extraStates):
            raise InvalidField(
                self.message('invalid', 'That is not a valid state code'),
                value, state)

    def _toPython(self, value, state):
        return string.strip(string.upper(value))

class PhoneNumber(FancyValidator):
    """
    Validates, and converts to ###-###-####, optionally with
    extension (as ext.##...)
    @@: should add internation phone number support
    """

    _phoneRE = re.compile(r'^\s*(?:1-)?(\d\d\d)[\- \.]?(\d\d\d)[\- \.]?(\d\d\d\d)(?:\s*ext\.?\s*(\d+))?\s*$', re.I)

    def _toPython(self, value, state):
        match = self._phoneRE.search(value)
        if not match:
            raise InvalidField(
                self.message('phoneFormat', 'Please enter a number, with area code, in the form ###-###-####, optionally with &quot;ext.####&quot;'),
                value, state)
        return value

    def _fromPython(self, value, state):
        if not isinstance(value, str):
            raise InvalidField('Invalid', value, state)
        match = self._phoneRE.search(value)
        if not match:
            raise InvalidField(self.message('phoneFormat', 'Please enter a number, with area code, in the form ###-###-####, optionally with &quot;ext.####&quot;'),
                               value, state)
        result = '%s-%s-%s' % (match.group(1), match.group(2), match.group(3))
        if match.group(4):
            result = result + " ext.%s" % match.group(4)
        return result

class DateConverter(FancyValidator):
    """
    Validates a textual date, like mm/yy, dd/mm/yy, dd-mm-yy, etc
    Always assumes month comes second value is the month.
    Accepts English month names, also abbreviated.
    Returns value as DateTime object.  Two year dates are assumed
    to be within 1950-2020, with dates from 21-49 being ambiguous
    and signaling an error.
    """

    _dayDateRE = re.compile(r'^\s*(\d\d?)[\-\./\\](\d\d?|jan|january|feb|febuary|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)[\-\./\\](\d\d\d?\d?)\s*$', re.I)
    _monthDateRE = re.compile(r'^\s*(\d\d?|jan|january|feb|febuary|mar|march|apr|april|may|jun|june|jul|july|aug|august|sep|sept|september|oct|october|nov|november|dec|december)[\-\./\\](\d\d\d?\d?)\s*$', re.I)

    _monthNames = {
        'jan': 1, 'january': 1,
        'feb': 2, 'febuary': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'sept': 9, 'september': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12,
        }

    ## @@: Feb. should be leap-year aware (but DateTime does catch that)
    _monthDays = {
        1: 31, 2: 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31,
        9: 30, 10: 31, 11: 30, 12: 31}

    def __init__(self, acceptDay=True, **kw):
        global DateTime
        if DateTime is None:
            try:
                from mx import DateTime
            except ImportError:
                import DateTime
        assert DateTime, "You must have mxDateTime installed to use DateConverter"
        self._acceptDay = acceptDay
        FancyValidator.__init__(self, **kw)

    def _toPython(self, value, state):
        if self._acceptDay: return self.convertDay(value, state)
        else: return self.convertMonth(value)

    def convertDay(self, value, state):
        match = self._dayDateRE.search(value)
        if not match:
            raise InvalidField(self.message('badFormat', 'Please enter the date in the form dd/mm/yyyy'), value, state)
        day = int(match.group(1))
        month = self.makeMonth(match.group(2))
        year = self.makeYear(match.group(3))
        if month > 12 or month < 1:
            raise InvalidField(self.message('monthRange', 'Please enter a month from 1 to 12'), value, state)
        if day < 1:
            raise InvalidField(self.message('invalidDay', 'Please enter a valid day'), value, state)
        if self._monthDays[month] < day:
            raise InvalidField(self.message('dayRange', 'That month only has %(days)i days') % {"days": self._monthDays[month]}, value, state)
        try:
            return DateTime.DateTime(year, month, day)
        except DateTime.RangeError, v:
            raise InvalidField(self.message('invalidDay', 'That is not a valid day') + '(%s)' % v, value, state)

    def makeMonth(self, value):
        try:
            return int(value)
        except ValueError:
            value = string.strip(string.lower(value))
            if self._monthNames.has_key(value):
                return self._monthNames[value]
            else:
                raise InvalidField(self.message('unknownMonthName', "Unknown month name: %(month)s") % {"month": value}, value, state)

    def makeYear(self, year):
        try:
            year = int(year)
        except ValueError:
            raise InvalidField(self.message('invalidYear', 'Please enter a number for the year'), value, state)
        if year <= 20:
            year = year + 2000
        if year >= 50 and year < 100:
            year = year + 1900
        if year > 20 and year < 50:
            raise InvalidField(self.message('fourDigitYear', 'Please enter a four-digit year'), value, state)
        return year

    def convertMonth(self, value, state):
        match = self._monthDateRE.search(value)
        if not match:
            raise InvalidField(self.message('wrongFormat', 'Please enter the date in the form mm/yyyy'), value, state)
        month = self.makeMonth(match.group(1))
        year = self.makeYear(match.group(2))
        if month > 12 or month < 1:
            raise InvalidField(self.message('monthRange', 'Please enter a month from 1 to 12'), value, state)
        return DateTime.DateTime(year, month)

    def _fromPython(self, value, state):
        if self._acceptDay: return self.unconvertDay(value, state)
        else: return self.unconvertMonth(value, state)

    def unconvertDay(self, value, state):
        # @@ ib: double-check, improve
        return value.strftime("%m/%d/%Y")

    def unconvertMonth(self, value, state):
        # @@ ib: double-check, improve
        return value.strftime("%m/%Y")

class PostalCode(Regex):

    def __init__(self, **kw):
        if not kw.setdefault('messages', {}).has_key('invalid'):
            kw['messages']['invalid'] = 'Please enter a zip code (5 digits)'
        Regex.__init__(self, r'^\d\d\d\d\d(?:-\d\d\d\d)?$', **kw)

class StripField(FancyValidator):

    """
    Take a field from a dictionary, removing the key from the dictionary.
    ``name`` is the key.
    """

    def __init__(self, name, **kw):
        self.name = name
        FancyValidator.__init__(self, **kw)

    def _toPython(self, valueDict, state):
        v = valueDict.copy()
        try:
            field = v[self.name]
            del v[self.name]
        except KeyError:
            raise InvalidField(self.message('missing', 'The name %(name)s is missing') % {'name': repr(self.name)}, valueDict, state)
        return field, v

class FormValidator(FancyValidator):
    """
    A FormValidator is something that can be chained with a
    Schema.  Unlike normal chaining the FormValidator can
    validate forms that aren't entirely valid.

    The important method is .validate(), of course.  It gets passed a
    dictionary of the (processed) values from the form.  If you have
    .validatePartialForm set to True, then it will get the incomplete
    values as well -- use .has_key() to test if the field was able to
    process any particular field.

    Anyway, .validate() should return a string or a dictionary.  If a
    string, it's an error message that applies to the whole form.  If
    not, then it should be a dictionary of fieldName: errorMessage.
    The special key "form" is the error message for the form as a whole
    (i.e., a string is equivalent to {"form": string}).

    Return None on no errors.
    """

    validatePartialForm = False

    validatePartialPython = None
    validatePartialOther = None

class FieldsMatch(FormValidator):

    def __init__(self, fieldNames, **kw):
        assert fieldNames, 'You must give at least one field name (though without two this is boring)'
        if kw.has_key('showMatch'):
            self._showMatch = kw['showMatch']
            del kw['showMatch']
        else:
            self._showMatch = False
        self._fieldNames = fieldNames
        FormValidator.__init__(self, **kw)

    validatePartialForm = True

    def validatePartial(self, fieldDict, state):
        for name in self._fieldNames:
            if not dict.has_key(name):
                return None
        self.validate(fieldDict)

    def validate(self, fieldDict, state):
        ref = fieldDict.get(self._fieldNames[0], '')
        errors = {}
        for name in self._fieldNames[1:]:
            if fieldDict.get(name, '') != ref:
                if self._showMatch:
                    errors[name] = self.message('invalid', "Fields do not match (should be %(match)s)") % {"match": ref}
                else:
                    errors[name] = self.message('invalidNoMatch', "Fields do not match")
        if errors:
            errorList = errors.items()
            errorList.sort()
            raise InvalidField('<br>\n'.join(['%s: %s' % (name, value) for name, value in errorList]),
                               fieldDict, state,
                               errorDict=errors)

class CreditCardValidator(FormValidator):
    """
    Checks that credit card numbers are valid (if not real).

    You pass in the name of the field that has the credit card
    type and the field with the credit card number.  The credit
    card type should be one of "visa", "mastercard", "amex",
    "dinersclub", "discover", "jcb".

    You must check the expiration date yourself (there is no
    relation between CC number/types and expiration dates).
    """

    def __init__(self, ccTypeField, ccNumberField, **kw):
        self._ccTypeField = ccTypeField
        self._ccNumberField = ccNumberField
        FormValidator.__init__(self, **kw)

    validatePartialForm = True

    def validatePartial(self, fieldDict, state):
        if not fieldDict.get(self._ccTypeField, None) \
           or not fieldDict.get(self._ccNumberField, None):
            return None
        self.validate(fieldDict, state)

    def validate(self, fieldDict, state):
        errors = self._validateReturn(fieldDict, state)
        if errors:
            errorList = errors.items()
            errorList.sort()
            raise InvalidField(
                '<br>\n'.join(["%s: %s" % (name, value)
                               for name, value in errorList]),
                fieldDict, state, errorDict=errors)

    def _validateReturn(self, fieldDict, state):
        ccType = string.lower(string.strip(fieldDict[self._ccTypeField]))
        number = string.strip(fieldDict[self._ccNumberField])
        number = string.replace(number, ' ', '')
        number = string.replace(number, '-', '')
        try:
            long(number)
        except ValueError:
            return {self._ccNumberField: self.message('invalidNumber', "Please enter only the number, no other characters")}

        assert _cardInfo.has_key(ccType), "I can't validate that type of credit card"
        foundValid = False
        validLength = False
        for prefix, length in self._cardInfo[ccType]:
            if len(number) == length:
                validLength = True
            if len(number) == length \
               and number[:len(prefix)] != prefix:
                foundValid = True
                break
        if not validLength:
            return {self._ccNumberField: self.message('badLength', "You did not enter a valid number of digits")}
        if not foundValid:
            return {self._ccNumberField: self.message('invalidNumber', "That number is not valid")}

        if not _validateMod10(number):
            return {self._ccNumberField: self.message('invalidNumber', "That number is not valid")}
        return None

    def _validateMod10(self, s):
        """
        This code by Sean Reifschneider, of tummy.com
        """
        double = 0
        sum = 0
        for i in range(len(s) - 1, -1, -1):
            for c in str((double + 1) * int(s[i])): sum = sum + int(c)
            double = (double + 1) % 2
        return((sum % 10) == 0)

    _cardInfo = {
        "visa": [('4', 16),
                 ('4', 13)],
        "mastercard": [('51', 16),
                       ('52', 16),
                       ('53', 16),
                       ('54', 16),
                       ('55', 16)],
        "discover": [('6011', 16)],
        "amex": [('34', 15),
                 ('37', 15)],
        "dinersclub": [('300', 14),
                       ('301', 14),
                       ('302', 14),
                       ('303', 14),
                       ('304', 14),
                       ('305', 14),
                       ('36', 14),
                       ('38', 14)],
        "jcb": [('3', 16),
                ('2131', 15),
                ('1800', 15)],
            }
