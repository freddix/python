%bcond_without	tests	# skip tests

# tests which will not work on 64-bit platforms
%define		no64bit_tests	test_audioop test_rgbimg test_imageop
# tests which may fail because of builder environment limitations (no /proc or /dev/pts)
%define		nobuilder_tests test_resource test_openpty test_socket test_nis test_posix test_locale test_pty test_urllib2 test_zlib
# tests which fail because of some unknown/unresolved reason (this list should be empty)
%define		broken_tests test_anydbm test_bsddb test_re test_shelve test_whichdb test_zipimport test_distutils test_pydoc

%define		py_dyndir	%{py_libdir}/lib-dynload
%define		py_incdir	%{_includedir}/python%{py_ver}
%define		py_libdir	%{_libdir}/python%{py_ver}
%define		py_scriptdir	%{_libdir}/python%{py_ver}
%define		py_sitedir	%{py_libdir}/site-packages
%define		py_ver		2.7

Summary:	Very high level scripting language with X interface
Name:		python
Version:	%{py_ver}.3
Release:	6
Epoch:		1
License:	PSF
Group:		Applications
Source0:	http://www.python.org/ftp/python/%{version}/Python-%{version}.tar.bz2
# Source0-md5:	c57477edd6d18bd9eeca2f21add73919
Patch0:		%{name}-pythonpath.patch
Patch1:		%{name}-ac_fixes.patch
Patch2:		%{name}-cflags.patch
Patch3:		%{name}-no-static-lib.patch
Patch4:		%{name}-lib64.patch
Patch5:		%{name}-lib64-regex.patch
Patch6:		%{name}-lib64-sysconfig.patch
URL:		http://www.python.org/
BuildRequires:	autoconf
BuildRequires:	bzip2-devel
BuildRequires:	db-devel
BuildRequires:	expat-devel
BuildRequires:	file
BuildRequires:	gdbm-devel
BuildRequires:	gmp-devel
BuildRequires:	libffi-devel
BuildRequires:	libstdc++-devel
BuildRequires:	ncurses-ext-devel
BuildRequires:	openssl-devel
BuildRequires:	readline-devel
BuildRequires:	rpm-pythonprov
BuildRequires:	sed
BuildRequires:	sqlite3-devel
BuildRequires:	zlib-devel
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		test_flags	-w -l -x
%define		test_list	%{nobuilder_tests} %{broken_tests}

%description
Python is an interpreted, interactive, object-oriented programming
language. It incorporates modules, exceptions, dynamic typing, very
high level dynamic data types, and classes. Python combines remarkable
power with very clear syntax. It has interfaces to many system calls
and libraries, as well as to various window systems, and is extensible
in C or C++. It is also usable as an extension language for
applications that need a programmable interface.

%package libs
Summary:	Python library
Group:		Libraries/Python
# broken detection in rpm/pythondeps.sh
Provides:	python(abi) = %{py_ver}
Provides:	python(bytecode) = %{py_ver}

%description libs
Python shared library and very essental modules for Python binary.

%package modules
Summary:	Python modules
Group:		Libraries/Python
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}

%description modules
Python officially distributed modules.

%package modules-sqlite
Summary:	Python SQLite module
Group:		Libraries/Python
Requires:	%{name}-modules = %{epoch}:%{version}-%{release}

%description modules-sqlite
Python SQLite module.

%package -n pydoc
Summary:	Python interactive module documentation access support
Group:		Applications
Requires:	%{name}-modules = %{epoch}:%{version}-%{release}
Obsoletes:	python-pydoc

%description -n pydoc
Python interactive module documentation access support.

%package devel
Summary:	Libraries and header files for building python code
Group:		Development/Languages/Python
Requires:	%{name}-libs = %{epoch}:%{version}-%{release}

%description devel
The Python interpreter is relatively easy to extend with dynamically
loaded extensions and to embed in other programs. This package
contains the header files and libraries which are needed to do both of
these tasks.

%package devel-src
Summary:	Python module sources
Group:		Development/Languages/Python
Requires:	%{name}-modules = %{epoch}:%{version}-%{release}

%description devel-src
Python module sources.

%package devel-tools
Summary:	Python development tools
Group:		Development/Languages/Python
Requires:	%{name}-modules = %{epoch}:%{version}-%{release}

%description devel-tools
Python development tools such as profilers and debugger.

%prep
%setup -qn Python-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

sed -i -e 's#db_setup_debug = False#db_setup_debug = True#g' setup.py

rm -r Modules/{expat,zlib,_ctypes/{darwin,libffi}*}

%build
%{__aclocal}
%{__autoconf}
CPPFLAGS="-I/usr/include/ncursesw %{rpmcppflags}"
export CPPFLAGS
%configure \
	ac_cv_posix_semaphores_enabled=yes	\
	ac_cv_broken_sem_getvalue=no		\
	--enable-ipv6				\
	--enable-shared				\
	--enable-unicode=ucs4			\
	--with-cxx-main="%{__cxx}"		\
	--with-dbmliborder=gdbm:bdb		\
	--with-system-expat			\
	--with-system-ffi			\
	--with-threads				\
	BLDSHARED='$(CC) $(CFLAGS) -shared'	\
	LDFLAGS="%{rpmcflags} %{rpmldflags}"	\
	LDSHARED='$(CC) $(CFLAGS) -shared'	\
	LINKCC='$(PURIFY) $(CXX)'

%{__make} 2>&1 | awk '
BEGIN { fail = 0; logmsg = ""; }
{
		if ($0 ~ /\*\*\* WARNING:/) {
				fail = 1;
				logmsg = logmsg $0;
		}
		print $0;
}
END { if (fail) { print "\nPROBLEMS FOUND:"; print logmsg; exit(1); } }'

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_libdir}} 	\
	$RPM_BUILD_ROOT{%{py_sitedir},%{_mandir}/man1}	\
	$RPM_BUILD_ROOT%{_infodir}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

ln -sf libpython%{py_ver}.so.1.0 $RPM_BUILD_ROOT%{_libdir}/libpython.so
ln -sf libpython%{py_ver}.so.1.0 $RPM_BUILD_ROOT%{_libdir}/libpython%{py_ver}.so

install Makefile.pre.in $RPM_BUILD_ROOT%{py_scriptdir}/config

%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/test
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/bsddb/test
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/ctypes/test
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/distutils/tests
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/email/test
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/sqlite3/test
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/json/tests
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/lib2to3/tests

%{__rm} -r $RPM_BUILD_ROOT%{_bindir}/idle
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/ctypes/macholib/fetch_macholib
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/distutils/command/command_template
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/idlelib
%{__rm} -r $RPM_BUILD_ROOT%{py_scriptdir}/lib-tk

find $RPM_BUILD_ROOT%{py_scriptdir} -name \*.egg-info -exec rm {} \;
find $RPM_BUILD_ROOT%{py_scriptdir} -name \*.bat -exec rm {} \;
find $RPM_BUILD_ROOT%{py_scriptdir} -name \*.txt -exec rm {} \;
find $RPM_BUILD_ROOT%{py_scriptdir} -name README\* -exec rm {} \;

%if %{with tests}
%check
%{__make} -j1 test \
        TESTOPTS="%{test_flags} %{test_list}" \
	TESTPYTHON="LD_LIBRARY_PATH=`pwd` PYTHONHOME=`pwd` PYTHONPATH=`pwd`/Lib:`pwd`/Lib/lib-tk:`pwd`/build/lib.linux-`uname -m`-%{py_ver} ./python -tt"
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /usr/sbin/ldconfig
%postun	libs -p /usr/sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/python
%attr(755,root,root) %{_bindir}/python2
%attr(755,root,root) %{_bindir}/python%{py_ver}
%{_mandir}/man1/python.1*

%files modules
%defattr(644,root,root,755)
%exclude %{py_scriptdir}/_abcoll.py[co]
%exclude %{py_scriptdir}/abc.py[co]
%exclude %{py_scriptdir}/UserDict.py[co]
%exclude %{py_scriptdir}/codecs.py[co]
%exclude %{py_scriptdir}/copy_reg.py[co]
%exclude %{py_scriptdir}/genericpath.py[co]
%exclude %{py_scriptdir}/linecache.py[co]
%exclude %{py_scriptdir}/locale.py[co]
%exclude %{py_scriptdir}/posixpath.py[co]
%exclude %{py_scriptdir}/pdb.py[co]
%exclude %{py_scriptdir}/profile.py[co]
%exclude %{py_scriptdir}/pstats.py[co]
%exclude %{py_scriptdir}/pydoc.py[co]
%exclude %{py_scriptdir}/re.py[co]
%exclude %{py_scriptdir}/site.py[co]
%exclude %{py_scriptdir}/sre_*.py[co]
%exclude %{py_scriptdir}/stat.py[co]
%exclude %{py_scriptdir}/sysconfig.py[co]
%exclude %{py_scriptdir}/timeit.py[co]
%exclude %{py_scriptdir}/os.py[co]
%exclude %{py_scriptdir}/_weakrefset.py[co]
%exclude %{py_scriptdir}/encodings/*.py[co]
%exclude %{py_scriptdir}/types.py[co]
%exclude %{py_scriptdir}/warnings.py[co]

%{py_scriptdir}/*.py[co]

# list .so modules to be sure that all of them are built
%attr(755,root,root) %{py_dyndir}/_bisect.so
%attr(755,root,root) %{py_dyndir}/_bsddb.so
%attr(755,root,root) %{py_dyndir}/_codecs_cn.so
%attr(755,root,root) %{py_dyndir}/_codecs_hk.so
%attr(755,root,root) %{py_dyndir}/_codecs_iso2022.so
%attr(755,root,root) %{py_dyndir}/_codecs_jp.so
%attr(755,root,root) %{py_dyndir}/_codecs_kr.so
%attr(755,root,root) %{py_dyndir}/_codecs_tw.so
%attr(755,root,root) %{py_dyndir}/_collections.so
%attr(755,root,root) %{py_dyndir}/_csv.so
%attr(755,root,root) %{py_dyndir}/_ctypes*.so
%attr(755,root,root) %{py_dyndir}/_curses.so
%attr(755,root,root) %{py_dyndir}/_curses_panel.so
%attr(755,root,root) %{py_dyndir}/_elementtree.so
%attr(755,root,root) %{py_dyndir}/_functools.so
%attr(755,root,root) %{py_dyndir}/_hashlib.so
%attr(755,root,root) %{py_dyndir}/_heapq.so
%attr(755,root,root) %{py_dyndir}/_io.so
%attr(755,root,root) %{py_dyndir}/_json.so
%attr(755,root,root) %{py_dyndir}/_locale.so
%attr(755,root,root) %{py_dyndir}/_lsprof.so
%attr(755,root,root) %{py_dyndir}/_multibytecodec.so
%attr(755,root,root) %{py_dyndir}/_multiprocessing.so
%attr(755,root,root) %{py_dyndir}/_random.so
%attr(755,root,root) %{py_dyndir}/_socket.so
%attr(755,root,root) %{py_dyndir}/_ssl.so
%attr(755,root,root) %{py_dyndir}/_testcapi.so
%attr(755,root,root) %{py_dyndir}/array.so
%attr(755,root,root) %{py_dyndir}/audioop.so
%attr(755,root,root) %{py_dyndir}/binascii.so
%attr(755,root,root) %{py_dyndir}/bz2.so
%attr(755,root,root) %{py_dyndir}/cPickle.so
%attr(755,root,root) %{py_dyndir}/cStringIO.so
%attr(755,root,root) %{py_dyndir}/cmath.so
%attr(755,root,root) %{py_dyndir}/crypt.so
%attr(755,root,root) %{py_dyndir}/datetime.so
%attr(755,root,root) %{py_dyndir}/dbm.so
%attr(755,root,root) %{py_dyndir}/fcntl.so
%attr(755,root,root) %{py_dyndir}/future_builtins.so
%attr(755,root,root) %{py_dyndir}/gdbm.so
%attr(755,root,root) %{py_dyndir}/grp.so
%attr(755,root,root) %{py_dyndir}/itertools.so
%attr(755,root,root) %{py_dyndir}/linuxaudiodev.so
%attr(755,root,root) %{py_dyndir}/math.so
%attr(755,root,root) %{py_dyndir}/mmap.so
%attr(755,root,root) %{py_dyndir}/nis.so
%attr(755,root,root) %{py_dyndir}/operator.so
%attr(755,root,root) %{py_dyndir}/parser.so
%attr(755,root,root) %{py_dyndir}/pyexpat.so
%attr(755,root,root) %{py_dyndir}/readline.so
%attr(755,root,root) %{py_dyndir}/resource.so
%attr(755,root,root) %{py_dyndir}/select.so
%attr(755,root,root) %{py_dyndir}/spwd.so
%attr(755,root,root) %{py_dyndir}/strop.so
%attr(755,root,root) %{py_dyndir}/syslog.so
%attr(755,root,root) %{py_dyndir}/termios.so
%attr(755,root,root) %{py_dyndir}/time.so
%attr(755,root,root) %{py_dyndir}/unicodedata.so
%attr(755,root,root) %{py_dyndir}/zlib.so

%ifnarch %{x8664}
%attr(755,root,root) %{py_dyndir}/dl.so
%attr(755,root,root) %{py_dyndir}/imageop.so
%endif

%dir %{py_scriptdir}/bsddb
%dir %{py_scriptdir}/compiler
%dir %{py_scriptdir}/ctypes
%dir %{py_scriptdir}/ctypes/macholib
%dir %{py_scriptdir}/curses
%dir %{py_scriptdir}/distutils
%dir %{py_scriptdir}/distutils/command
%dir %{py_scriptdir}/email
%dir %{py_scriptdir}/email/mime
%dir %{py_scriptdir}/importlib
%dir %{py_scriptdir}/json
%dir %{py_scriptdir}/logging
%dir %{py_scriptdir}/multiprocessing
%dir %{py_scriptdir}/multiprocessing/dummy
%dir %{py_scriptdir}/plat-*
%dir %{py_scriptdir}/unittest
%dir %{py_scriptdir}/unittest/test
%dir %{py_scriptdir}/wsgiref
%dir %{py_scriptdir}/xml
%dir %{py_scriptdir}/xml/dom
%dir %{py_scriptdir}/xml/etree
%dir %{py_scriptdir}/xml/parsers
%dir %{py_scriptdir}/xml/sax
%{py_scriptdir}/bsddb/*.py[co]
%{py_scriptdir}/compiler/*.py[co]
%{py_scriptdir}/ctypes/*.py[co]
%{py_scriptdir}/ctypes/macholib/*.py[co]
%{py_scriptdir}/curses/*.py[co]
%{py_scriptdir}/distutils/*.py[co]
%{py_scriptdir}/distutils/command/*.py[co]
%{py_scriptdir}/email/*.py[co]
%{py_scriptdir}/email/mime/*.py[co]
%{py_scriptdir}/importlib/*.py[co]
%{py_scriptdir}/json/*.py[co]
%{py_scriptdir}/logging/*.py[co]
%{py_scriptdir}/multiprocessing/*.py[co]
%{py_scriptdir}/multiprocessing/dummy/*.py[co]
%{py_scriptdir}/plat-*/*.py[co]
%{py_scriptdir}/unittest/*.py[co]
%{py_scriptdir}/unittest/test/*.py[co]
%{py_scriptdir}/wsgiref/*.py[co]
%{py_scriptdir}/xml/*.py[co]
%{py_scriptdir}/xml/dom/*.py[co]
%{py_scriptdir}/xml/etree/*.py[co]
%{py_scriptdir}/xml/parsers/*.py[co]
%{py_scriptdir}/xml/sax/*.py[co]

%files modules-sqlite
%defattr(644,root,root,755)
%dir %{py_scriptdir}/sqlite3
%attr(755,root,root) %{py_dyndir}/_sqlite3.so
%{py_scriptdir}/sqlite3/*.py[co]

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libpython*.so.*

%dir %{py_dyndir}
%dir %{py_scriptdir}
%dir %{py_libdir}
%dir %{py_sitescriptdir}
%dir %{py_sitedir}

# shared modules required by python library
%attr(755,root,root) %{py_dyndir}/_struct.so

# modules required by python library
%{py_scriptdir}/_abcoll.py[co]
%{py_scriptdir}/abc.py[co]
%{py_scriptdir}/UserDict.py[co]
%{py_scriptdir}/codecs.py[co]
%{py_scriptdir}/copy_reg.py[co]
%{py_scriptdir}/genericpath.py[co]
%{py_scriptdir}/linecache.py[co]
%{py_scriptdir}/locale.py[co]
%{py_scriptdir}/posixpath.py[co]
%{py_scriptdir}/re.py[co]
%{py_scriptdir}/site.py[co]
%{py_scriptdir}/sre_*.py[co]
%{py_scriptdir}/stat.py[co]
%{py_scriptdir}/sysconfig.py[co]
%{py_scriptdir}/os.py[co]
%{py_scriptdir}/_weakrefset.py[co]
# needed by the dynamic sys.lib patch
%{py_scriptdir}/types.py[co]
%{py_scriptdir}/warnings.py[co]

# encodings required by python library
%dir %{py_scriptdir}/encodings
%{py_scriptdir}/encodings/*.py[co]

# required by sysconfig.py
%dir %{py_scriptdir}/config
%{py_scriptdir}/config/Makefile
%dir %{py_incdir}
%{py_incdir}/pyconfig.h

%files -n pydoc
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/pydoc
%{py_scriptdir}/pydoc.py[co]
%dir %{py_scriptdir}/pydoc_data
%{py_scriptdir}/pydoc_data/*.py[co]

%files devel
%defattr(644,root,root,755)
%doc Misc/{ACKS,NEWS,README,README.valgrind,valgrind-python.supp}
%attr(755,root,root) %{_bindir}/python-config
%attr(755,root,root) %{_bindir}/python2-config
%attr(755,root,root) %{_bindir}/python%{py_ver}-config
%attr(755,root,root) %{_libdir}/lib*.so
%dir %{py_incdir}
%{py_incdir}/*.h
%exclude %{py_incdir}/pyconfig.h
%{_pkgconfigdir}/python.pc
%{_pkgconfigdir}/python2.pc
%{_pkgconfigdir}/python-%{py_ver}.pc

%dir %{py_scriptdir}/config
%attr(755,root,root) %{py_scriptdir}/config/makesetup
%attr(755,root,root) %{py_scriptdir}/config/install-sh
%{py_scriptdir}/config/Makefile.pre.in
%{py_scriptdir}/config/Setup
%{py_scriptdir}/config/Setup.config
%{py_scriptdir}/config/Setup.local
%{py_scriptdir}/config/config.c
%{py_scriptdir}/config/config.c.in
%{py_scriptdir}/config/python.o

%files devel-src
%defattr(644,root,root,755)
%attr(-,root,root) %{py_scriptdir}/*.py
%{py_scriptdir}/plat-*/*.py
%{py_scriptdir}/bsddb/*.py
%{py_scriptdir}/compiler/*.py
%{py_scriptdir}/ctypes/*.py
%{py_scriptdir}/ctypes/macholib/*.py
%{py_scriptdir}/curses/*.py
%{py_scriptdir}/distutils/*.py
%{py_scriptdir}/distutils/command/*.py
%{py_scriptdir}/email/*.py
%{py_scriptdir}/email/mime/*.py
%{py_scriptdir}/encodings/*.py
%{py_scriptdir}/hotshot/*.py
%{py_scriptdir}/importlib/*.py
%{py_scriptdir}/json/*.py
%{py_scriptdir}/lib2to3/*.py
%{py_scriptdir}/lib2to3/fixes/*.py
%{py_scriptdir}/lib2to3/pgen2/*.py
%{py_scriptdir}/logging/*.py
%{py_scriptdir}/multiprocessing/*.py
%{py_scriptdir}/multiprocessing/dummy/*.py
%{py_scriptdir}/pydoc_data/*.py
%{py_scriptdir}/sqlite3/*.py
%{py_scriptdir}/unittest/*.py
%{py_scriptdir}/unittest/test/*.py
%{py_scriptdir}/wsgiref/*.py
%{py_scriptdir}/xml/*.py
%{py_scriptdir}/xml/dom/*.py
%{py_scriptdir}/xml/etree/*.py
%{py_scriptdir}/xml/parsers/*.py
%{py_scriptdir}/xml/sax/*.py

%files devel-tools
%defattr(644,root,root,755)
%doc Lib/pdb.doc
%attr(755,root,root) %{_bindir}/2to3
%attr(755,root,root) %{py_dyndir}/_hotshot.so

%dir %{py_scriptdir}/hotshot
%dir %{py_scriptdir}/lib2to3
%dir %{py_scriptdir}/lib2to3/fixes
%dir %{py_scriptdir}/lib2to3/pgen2

%{py_scriptdir}/hotshot/*.py[co]
%{py_scriptdir}/lib2to3/*.pickle
%{py_scriptdir}/lib2to3/*.py[co]
%{py_scriptdir}/lib2to3/fixes/*.py[co]
%{py_scriptdir}/lib2to3/pgen2/*.py[co]
%{py_scriptdir}/pdb.py[co]
%{py_scriptdir}/profile.py[co]
%{py_scriptdir}/pstats.py[co]
%{py_scriptdir}/timeit.py[co]

