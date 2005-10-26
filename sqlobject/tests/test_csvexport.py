from sqlobject import *
from dbtest import *
import csv
from StringIO import StringIO
from sqlobject.util.csvexport import export_csv, export_csv_zip

def assert_export(result, *args, **kw):
    f = StringIO()
    kw['writer'] = f
    export_csv(*args, **kw)
    s = f.getvalue().replace('\r\n', '\n')
    if result.strip() != s.strip():
        print '**Expected:'
        print result
        print '**Got:'
        print s
        assert result.strip() == s.strip()

class Simple(SQLObject):

    name = StringCol()
    address = StringCol()
    address.csvTitle = 'Street Address'
    hidden = StringCol()
    hidden.noCSV = True

class Complex(SQLObject):
    
    fname = StringCol()
    lname = StringCol()
    age = IntCol()
    extraCSVColumns = [('name', 'Full Name'), 'initials']
    # initials should end up at the end then:
    csvColumnOrder = ['name', 'fname', 'lname', 'age']
    def _get_name(self):
        return self.fname + ' ' + self.lname
    def _get_initials(self):
        return self.fname[0] + self.lname[0]
    
def test_simple():
    setupClass(Simple)
    Simple(name='Bob', address='432W', hidden='boo')
    Simple(name='Joe', address='123W', hidden='arg')
    assert_export("""\
name,Street Address
Bob,432W
Joe,123W
""", Simple, orderBy='name')
    assert_export("""\
name,Street Address
Joe,123W
Bob,432W
""", Simple, orderBy='address')
    assert_export("""\
name,Street Address
Joe,123W
""", Simple.selectBy(name='Joe'))
    
def test_complex():
    setupClass(Complex)
    Complex(fname='John', lname='Doe', age=40)
    Complex(fname='Bob', lname='Dylan', age=60)
    Complex(fname='Harriet', lname='Tubman', age=160)
    assert_export("""\
Full Name,fname,lname,age,initials
John Doe,John,Doe,40,JD
Bob Dylan,Bob,Dylan,60,BD
Harriet Tubman,Harriet,Tubman,160,HT
""", Complex, orderBy='lname')
    assert_export("""\
Full Name,fname,lname,age,initials
Bob Dylan,Bob,Dylan,60,BD
John Doe,John,Doe,40,JD
""", Complex.select(Complex.q.lname.startswith('D'), orderBy='fname'))

def test_zip():
    # Just exercise tests, doesn't actually test results
    setupClass(Simple)
    Simple(name='Bob', address='432W', hidden='boo')
    Simple(name='Joe', address='123W', hidden='arg')
    
    setupClass(Complex)
    Complex(fname='John', lname='Doe', age=40)
    Complex(fname='Bob', lname='Dylan', age=60)
    Complex(fname='Harriet', lname='Tubman', age=160)
    s = export_csv_zip([Simple, Complex])
    assert isinstance(s, str) and s
    s = export_csv_zip([Simple.selectBy(name='Bob'),
                        (Complex, list(Complex.selectBy(fname='John')))])
    
