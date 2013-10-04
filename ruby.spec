%define _buildid .53

%bcond_with X11

%global major_version 1
%global minor_version 9
%global teeny_version 3
%global patch_level 448

%global priority %{major_version}%{minor_version}%{teeny_version}

%global base_name ruby
# define base_ver only if you want to build a secondary package instead of a main package
# (ie, ruby19-1.9.x instead of ruby-1.9.x)
%global base_ver                 %{major_version}%{minor_version}
%global base_dotver              %{major_version}.%{minor_version}

%global ruby_version             %{major_version}.%{minor_version}.%{teeny_version}
%global ruby_version_patch_level %{major_version}.%{minor_version}.%{teeny_version}.%{patch_level}
%global ruby_abi                 %{major_version}.%{minor_version}.1

%global ruby_archive             ruby-%{ruby_version}-p%{patch_level}

%global ruby_libdir              %{_datadir}/%{base_name}/%{base_dotver}
%global ruby_libarchdir          %{_libdir}/%{base_name}/%{base_dotver}

# This is the local lib/arch and should not be used for packaging.
# Currently using Ruby's default, this should be changed as to avoid
# conflicts with other version
%global ruby_sitedir             site_ruby
%global ruby_sitelibdir          %{_prefix}/local/share/%{name}/%{ruby_sitedir}
%global ruby_sitearchdir         %{_prefix}/local/%{_lib}/%{name}/%{ruby_sitedir}

# This is the general location for libs/archs compatible with all
# or most of the Ruby versions available in the Fedora repositories.
%global ruby_vendordir           vendor_ruby
%global ruby_vendorlibdir        %{ruby_libdir}/%{ruby_vendordir}
%global ruby_vendorarchdir       %{ruby_libarchdir}/%{ruby_vendordir}

%global rubygems_version         1.8.23

# The RubyGems library has to stay out of Ruby directory three, since the
# RubyGems should be share by all Ruby implementations.
%global rubygems_dir             %{_datadir}/rubygems%{base_dotver}

# Specify custom RubyGems root.
%global gem_dir                  %{_datadir}/gems%{base_dotver}
# TODO: Should we create arch specific rubygems-filesystem?
%global gem_extdir               %{_libdir}/gems%{base_dotver}/exts

%global rake_version             0.9.2.2
# TODO: The IRB has strange versioning. Keep the Ruby's versioning ATM.
# http://redmine.ruby-lang.org/issues/5313
%global irb_version              %{ruby_version_patch_level}
%global rdoc_version             3.9.5
%global bigdecimal_version       1.1.0
%global io_console_version       0.3
%global json_version             1.5.5
%global minitest_version         2.5.1

%global	_normalized_cpu	%(echo %{_target_cpu} | sed 's/^ppc/powerpc/;s/i.86/i386/;s/sparcv./sparc/')

Summary: An interpreter of object-oriented scripting language
Name: %{base_name}%{base_ver}
Version: %{ruby_version_patch_level}
# Note:
# As seen on perl srpm, as this (ruby) srpm contains several sub-components,
# we cannot reset the release number to 1 even when the main (ruby) version
# is updated - because it may be that the versions of sub-components don't
# change.
Release: 31%{?_buildid}%{?dist}
Group: Development/Languages
# Public Domain for example for: include/ruby/st.h, strftime.c, ...
License: (Ruby or BSD) and Public Domain
URL: http://ruby-lang.org/
Source0: ftp://ftp.ruby-lang.org/pub/%{base_name}/%{major_version}.%{minor_version}/%{ruby_archive}.tar.gz
Source1: operating_system.rb

# http://redmine.ruby-lang.org/issues/5231
Patch0: ruby-1.9.3-disable-versioned-paths.patch
# TODO: Should be submitted upstream?
Patch1: ruby-1.9.3-arch-specific-dir.patch
# http://redmine.ruby-lang.org/issues/5281
Patch2: ruby-1.9.3-added-site-and-vendor-arch-flags.patch
# Force multiarch directories for i.86 to be always named i386. This solves
# some differencies in build between Fedora and RHEL.
Patch3: ruby-1.9.3-always-use-i386.patch
# http://redmine.ruby-lang.org/issues/5465
# Fixed in 1.9.3 p448
#Patch4: ruby-1.9.3-fix-s390x-build.patch
# Fix the uninstaller, so that it doesn't say that gem doesn't exist
# when it exists outside of the GEM_HOME (already fixed in the upstream)
Patch5: ruby-1.9.3-rubygems-1.8.11-uninstaller.patch
# Allows to install RubyGems into custom directory, outside of Ruby's tree.
# http://redmine.ruby-lang.org/issues/5617
Patch8: ruby-1.9.3-custom-rubygems-location.patch
# Add support for installing binary extensions according to FHS.
# https://github.com/rubygems/rubygems/issues/210
Patch9: rubygems-1.8.11-binary-extensions.patch
# Opening /dev/tty fails with ENXIO (ref: man 2 open) on koji.
# Let's rescue this
# Fixed in ruby 1.9.3 p327
#Patch10: ruby-1.9.3-p286-open-devtty-on-koji.patch
# On koji, network related tests sometimes cause internal server error,
# ignore these
Patch10: ruby-1.9.3-p327-ignore-internal-server-error-on-test.patch
# http://bugs.ruby-lang.org/issues/show/7312
# test_str_crypt fails with glibc 2.17
# Fixed in 1.9.3 p 362
#Patch11: ruby-1.9.3-p327-crypt-argument-glibc217.patch
# Make mkmf verbose by default
Patch12: ruby-1.9.3-mkmf-verbose.patch
# http://bugs.ruby-lang.org/issues/7629
# https://bugzilla.redhat.com/show_bug.cgi?id=895173
# save the proc made from the given block
# Fixed in p374
#Patch13: ruby-1.9.3-p327-PR7629-save-proc.patch
# Fixes issues mentioned in rhbz#789532, comment 8.
# TODO: Should be probably upstreamed with #5281.
Patch14: ruby-2.0.0-Expand-ruby.pc-variable-by-configuration-process.patch

# Amazon build fixes
Patch200: ruby-1.9-autoconf.patch
Patch201: rdoc19-sort-file-list.patch
Patch202: ruby-1.9-fix-test_timeout.patch
Patch203: rubygems-1.8.25-CVE-2013-4287.patch

Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: rubygems%{base_ver} >= %{rubygems_version}
# Make the bigdecimal gem a runtime dependency of Ruby to avoid problems
# with user-installed gems, that don't require it in gemspec/Gemfile
# See https://bugzilla.redhat.com/show_bug.cgi?id=829209
# and http://bugs.ruby-lang.org/issues/6123
Requires: rubygem%{base_ver}-bigdecimal%{?_isa} >= %{bigdecimal_version}

Requires(post):  %{_sbindir}/update-alternatives
Requires(preun): %{_sbindir}/update-alternatives

BuildRequires: autoconf
BuildRequires: gdbm-devel
BuildRequires: ncurses-devel
%if 0%{?fedora} >= 19
BuildRequires: libdb-devel
%else
BuildRequires: db4-devel
%endif
%if 0%{?rhel} > 5 || 0%{?amzn}
BuildRequires: libffi-devel
%endif
BuildRequires: openssl-devel
BuildRequires: libyaml-devel
BuildRequires: readline-devel
%if %{with X11}
BuildRequires: tk-devel
%endif
# Needed to pass test_set_program_name(TestRubyOptions)
BuildRequires: procps
Provides: %{base_name}                       = %{version}-%{release}
Provides: %{base_name}%{?_isa}               = %{version}-%{release}
Provides: %{base_name}%{base_dotver}         = %{version}-%{release}
Provides: %{base_name}%{base_dotver}%{_?isa} = %{version}-%{release}

# for capi documentation
BuildRequires: doxygen


%if 0%{?rhel} < 6 && !0%{?amzn}
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
%endif

%description
Ruby is the interpreted scripting language for quick and easy
object-oriented programming.  It has many features to process text
files and to do system management tasks (as in Perl).  It is simple,
straight-forward, and extensible.


%package devel
Summary:    A Ruby development environment
Group:      Development/Languages
Requires:   %{name}%{?_isa} = %{version}-%{release}

%description devel
Header files and libraries for building an extension library for the
Ruby or an application embedding Ruby.

%package libs
Summary:    Libraries necessary to run Ruby
Group:      Development/Libraries
License:    Ruby or BSD
Provides:   ruby(abi) = %{ruby_abi}

%description libs
This package includes the libruby, necessary to run Ruby.

# TODO: Rename or not rename to ruby-rubygems?
%package -n rubygems%{base_ver}
Summary:    The Ruby standard for packaging ruby libraries
Version:    %{rubygems_version}
Group:      Development/Libraries
License:    Ruby or MIT
Requires:   ruby(abi)                      = %{ruby_abi}
Requires:   rubygem%{base_ver}-rdoc       >= %{rdoc_version}
Requires:   rubygem%{base_ver}-io-console >= %{io_console_version}
Provides:   gem                            = %{rubygems_version}
Provides:   gem%{base_dotver}              = %{rubygems_version}
Provides:   ruby(rubygems)                 = %{rubygems_version}
Provides:   ruby%{base_dotver}(rubygems)   = %{rubygems_version}
Provides:   rubygems                       = %{rubygems_version}
Provides:   rubygems%{base_ver}            = %{rubygems_version}
%if 0%{?rhel} > 5 || 0%{?amzn}
BuildArch:  noarch
%endif

%description -n rubygems%{?base_ver}
RubyGems is the Ruby standard for publishing and managing third party
libraries.


%package -n rubygems%{base_ver}-devel
Summary:    Macros and development tools for packaging RubyGems
Version:    %{rubygems_version}
Group:      Development/Libraries
License:    Ruby or MIT
Requires:   rubygems%{base_ver}          = %{rubygems_version}
Provides:   rubygems-devel               = %{rubygems_version}
Provides:   rubygems%{base_dotver}-devel = %{rubygems_version}
%if 0%{?rhel} > 5 || 0%{?amzn}
BuildArch:  noarch
%endif

%description -n rubygems%{base_ver}-devel
Macros and development tools for packaging RubyGems.


%package -n rubygem%{base_ver}-rake
Summary:    Ruby based make-like utility
Version:    %{rake_version}
Group:      Development/Libraries
License:    Ruby or MIT
Requires:   ruby(abi)                    = %{ruby_abi}
Requires:   rubygems%{base_ver}         >= %{rubygems_version}
Provides:   rake                         = %{rake_version}
Provides:   rake%{base_dotver}           = %{rake_version}
Provides:   rubygem(rake)                = %{rake_version}
Provides:   rubygem%{base_dotver}(rake)  = %{rake_version}
Provides:   rubygem-rake                 = %{rake_version}
Provides:   rubygem%{base_dotver}-rake   = %{rake_version}
%if 0%{?rhel} > 5 || 0%{?amzn}
BuildArch:  noarch
%endif

%description -n rubygem%{base_ver}-rake
Rake is a Make-like program implemented in Ruby. Tasks and dependencies are
specified in standard Ruby syntax.


%package irb
Summary:    The Interactive Ruby
Version:    %{irb_version}
Group:      Development/Libraries
Requires:   ruby(abi)                      = %{ruby_abi}
Provides:   irb                            = %{irb_version}
Provides:   irb%{base_dotver}              = %{irb_version}
Provides:   ruby(irb)                      = %{irb_version}
Provides:   ruby%{base_dotver}(irb)        = %{irb_version}
Provides:   %{base_name}-irb               = %{irb_version}
Provides:   %{base_name}%{base_dotver}-irb = %{irb_version}
%if 0%{?rhel} > 5 || 0%{?amzn}
BuildArch:  noarch
%endif

%description irb
The irb is acronym for Interactive Ruby.  It evaluates ruby expression
from the terminal.


%package -n rubygem%{base_ver}-rdoc
Summary:    A tool to generate HTML and command-line documentation for Ruby projects
Version:    %{rdoc_version}
Group:      Development/Libraries
License:    GPLv2 and Ruby and MIT
Requires:   ruby(abi)                   = %{ruby_abi}
Requires:   rubygems%{base_ver}        >= %{rubygems_version}
Requires:   %{name}-irb                 = %{irb_version}
Provides:   rdoc                        = %{rdoc_version}
Provides:   rdoc%{base_dotver}          = %{rdoc_version}
Provides:   ri                          = %{rdoc_version}
Provides:   ri%{base_dotver}            = %{rdoc_version}
Provides:   rubygem(rdoc)               = %{rdoc_version}
Provides:   rubygem%{base_dotver}(rdoc) = %{rdoc_version}
Provides:   rubygem-rdoc                = %{rdoc_version}
Provides:   rubygem%{base_dotver}-rdoc  = %{rdoc_version}
# Should only be turned on when we want to get rid of Ruby 1.8
# Obsoletes:  ruby-rdoc < %{version}
# Obsoletes:  ruby-ri < %{version}
%if 0%{?rhel} > 5 || 0%{?amzn}
BuildArch:  noarch
%endif

%description -n rubygem%{base_ver}-rdoc
RDoc produces HTML and command-line documentation for Ruby projects.  RDoc
includes the 'rdoc' and 'ri' tools for generating and displaying online
documentation.


%package doc
Summary:    Documentation for %{name}
Group:      Documentation
Requires:   %{_bindir}/ri%{base_dotver}
Provides:   %{base_name}-doc = %{version}-%{release}
# TODO: It seems that ri documentation differs from platform to platform due to
# some encoding bugs, therefore the documentation should be split out of this gem
# or kept platform specific.
# https://github.com/rdoc/rdoc/issues/71
# BuildArch:  noarch

%description doc
This package contains documentation for %{name}.


%package -n rubygem%{base_ver}-bigdecimal
Summary:    BigDecimal provides arbitrary-precision floating point decimal arithmetic
Version:    %{bigdecimal_version}
Group:      Development/Libraries
License:    GPL+ or Artistic
Requires:   %{name}-libs%{?_isa}                     = %{ruby_version_patch_level}-%{release}
Requires:   rubygems%{base_ver}                     >= %{rubygems_version}
Provides:   rubygem(bigdecimal)                      = %{bigdecimal_version}
Provides:   rubygem%{base_dotver}(bigdecimal)        = %{bigdecimal_version}
Provides:   rubygem-bigdecimal                       = %{bigdecimal_version}
Provides:   rubygem%{base_dotver}-bigdecimal         = %{bigdecimal_version}
Provides:   rubygem-bigdecimal%{?_isa}               = %{bigdecimal_version}
Provides:   rubygem%{base_dotver}-bigdecimal%{?_isa} = %{bigdecimal_version}

%description -n rubygem%{base_ver}-bigdecimal
Ruby provides built-in support for arbitrary precision integer arithmetic.
For example:

42**13 -> 1265437718438866624512

BigDecimal provides similar support for very large or very accurate floating
point numbers. Decimal arithmetic is also useful for general calculation,
because it provides the correct answers people expect–whereas normal binary
floating point arithmetic often introduces subtle errors because of the
conversion between base 10 and base 2.


%package -n rubygem%{base_ver}-io-console
Summary:    IO/Console is a simple console utilizing library
Version:    %{io_console_version}
Group:      Development/Libraries
Requires:   %{name}-libs%{?_isa}                     = %{ruby_version_patch_level}-%{release}
Requires:   rubygems%{base_ver}                     >= %{rubygems_version}
Provides:   rubygem(io-console)                      = %{io_console_version}
Provides:   rubygem%{base_dotver}(io-console)        = %{io_console_version}
Provides:   rubygem-io-console                       = %{io_console_version}
Provides:   rubygem%{base_dotver}-io-console         = %{io_console_version}
Provides:   rubygem-io-console%{?_isa}               = %{io_console_version}
Provides:   rubygem%{base_dotver}-io-console%{?_isa} = %{io_console_version}

%description -n rubygem%{base_ver}-io-console
IO/Console provides very simple and portable access to console. It doesn't
provide higher layer features, such like curses and readline.


%package -n rubygem%{base_ver}-json
Summary:    This is a JSON implementation as a Ruby extension in C
Version:    %{json_version}
Group:      Development/Libraries
License:    Ruby or GPLv2
Requires:   %{name}-libs%{?_isa}               = %{ruby_version_patch_level}-%{release}
Requires:   rubygems%{base_ver}               >= %{rubygems_version}
Provides:   rubygem(json)                      = %{json_version}
Provides:   rubygem%{base_dotver}(json)        = %{json_version}
Provides:   rubygem-json                       = %{json_version}
Provides:   rubygem%{base_dotver}-json         = %{json_version}
Provides:   rubygem-json%{?_isa}               = %{json_version}
Provides:   rubygem%{base_dotver}-json%{?_isa} = %{json_version}

%description -n rubygem%{base_ver}-json
This is a implementation of the JSON specification according to RFC 4627.
You can think of it as a low fat alternative to XML, if you want to store
data to disk or transmit it over a network rather than use a verbose
markup language.


%package -n rubygem%{base_ver}-minitest
Summary:    Minitest provides a complete suite of testing facilities.
Version:    %{minitest_version}
Group:      Development/Libraries
License:    MIT
Requires:   ruby(abi)                        = %{ruby_abi}
Requires:   rubygems%{base_ver}             >= %{rubygems_version}
Provides:   rubygem(minitest)                = %{minitest_version}
Provides:   rubygems%{base_dotver}(minitest) = %{minitest_version}
Provides:   rubygem-minitest                 = %{minitest_version}
Provides:   rubygem%{base_dotver}-minitest   = %{minitest_version}
%if 0%{?rhel} > 5 || 0%{?amzn}
BuildArch:  noarch
%endif

%description -n rubygem%{base_ver}-minitest
minitest/unit is a small and incredibly fast unit testing framework.

minitest/spec is a functionally complete spec engine.

minitest/benchmark is an awesome way to assert the performance of your
algorithms in a repeatable manner.

minitest/mock by Steven Baker, is a beautifully tiny mock object
framework.

minitest/pride shows pride in testing and adds coloring to your test
output.

%if %{with X11}
%package tcltk
Summary:    Tcl/Tk interface for scripting language Ruby
Group:      Development/Languages
Requires:   %{name}-libs%{?_isa}                     = %{version}-%{release}
Provides:   ruby(tcltk)                              = %{version}-%{release}
Provides:   ruby%{base_dotver}(tcltk)                = %{version}-%{release}
Provides:   %{base_name}-tcltk                       = %{version}-%{release}
Provides:   %{base_name}%{base_dotver}-tcltk         = %{version}-%{release}
Provides:   %{base_name}-tcltk%{?_isa}               = %{version}-%{release}
Provides:   %{base_name}%{base_dotver}-tcltk%{?_isa} = %{version}-%{release}

%description tcltk
Tcl/Tk interface for the object-oriented scripting language Ruby.
%endif

%prep
%setup -q -n %{ruby_archive}

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
#%%patch4 -p1
%patch5 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
#%%patch11 -p1
%patch12 -p1
#%%patch13 -p1
%patch14 -p1

%if 0%{?rhel} < 6 && !0%{?amzn}
%patch200 -p1
%endif

%patch201 -p1
%patch202 -p1
%patch203 -p1

%build
autoconf

%configure \
        --disable-werror \
        --with-rubylibprefix='%{ruby_libdir}' \
        --with-archdir='%{ruby_libarchdir}' \
        --with-sitedir='%{ruby_sitelibdir}' \
        --with-sitearchdir='%{ruby_sitearchdir}' \
        --with-vendordir='%{ruby_vendorlibdir}' \
        --with-vendorarchdir='%{ruby_vendorarchdir}' \
        --with-rubyhdrdir='%{_includedir}/%{base_name}%{base_dotver}' \
        --with-vendorhdrdir='%{_includedir}/%{base_name}%{base_dotver}' \
        --with-sitehdrdir='%{_includedir}/%{base_name}%{base_dotver}' \
        --with-ridir='%{_datadir}/ri/%{base_dotver}' \
        --disable-versioned-paths \
        --with-rubygemsdir='%{rubygems_dir}' \
        --with-ruby_pc='%{base_name}-%{base_dotver}.pc' \
        --disable-rpath \
        --enable-shared \
	--program-suffix=%{base_dotver} \
%if ! %{with X11}
        --without-X11 \
%endif
%{nil}

# Q= makes the build output more verbose and allows to check Fedora
# compiler options.

# sadly, the ruby Makefiles are prone to race conditions and non-deterministic
# output when run with parallel make
#make %{?_smp_mflags} COPY="cp -p" Q=
make COPY="cp -p" Q=

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

# Dump the macros into macro.ruby to use them to build other Ruby libraries.
mkdir -p %{buildroot}%{_sysconfdir}/rpm
cat >> %{buildroot}%{_sysconfdir}/rpm/macros.%{name} << \EOF
%%ruby_libdir        %{ruby_libdir}
%%ruby_libarchdir    %{ruby_libarchdir}

# This is the local lib/arch and should not be used for packaging.
%%ruby_sitelibdir    %{ruby_sitelibdir}
%%ruby_sitearchdir   %{ruby_sitearchdir}

# This is the general location for libs/archs compatible with all
# or most of the Ruby versions available in the Fedora repositories.
%%ruby_vendorlibdir  %{ruby_vendorlibdir}
%%ruby_vendorarchdir %{ruby_vendorarchdir}
EOF

cat >> %{buildroot}%{_sysconfdir}/rpm/macros.%{name}gems << \EOF
# The RubyGems root folder.
%%gem_dir     %{gem_dir}

# Common gem locations and files.
%%gem_instdir %%{gem_dir}/gems/%%{gem_name}-%%{version}
%%gem_extdir  %{gem_extdir}/%%{gem_name}-%%{version}
%%gem_libdir  %%{gem_instdir}/lib
%%gem_cache   %%{gem_dir}/cache/%%{gem_name}-%%{version}.gem
%%gem_spec    %%{gem_dir}/specifications/%%{gem_name}-%%{version}.gemspec
%%gem_docdir  %%{gem_dir}/doc/%%{gem_name}-%%{version}
EOF

# Install custom operating_system.rb.
mkdir -p %{buildroot}%{rubygems_dir}/rubygems/defaults
cp %{SOURCE1} %{buildroot}%{rubygems_dir}/rubygems/defaults

# Move gems root into common directory, out of Ruby directory structure.
mkdir -p %{buildroot}%{gem_dir}
mv %{buildroot}%{ruby_libdir}/gems/%{ruby_abi}/* %{buildroot}%{gem_dir}
rm -rf %{buildroot}%{ruby_libdir}/gems

# Create folders for gem binary extensions.
# (need to create both lib and lib64 so the noarch packages will have the same manifest)
mkdir -p %{buildroot}%{_exec_prefix}/lib{,64}/gems%{base_dotver}/exts
mkdir -p %{buildroot}%{gem_extdir}

# Move bundled rubygems to %%gem_dir and %%gem_extdir
# make symlinks for io-console and bigdecimal, which are considered to be part of stdlib by other Gems
mkdir -p %{buildroot}%{gem_dir}/gems/rake-%{rake_version}/lib
mv %{buildroot}%{ruby_libdir}/rake* %{buildroot}%{gem_dir}/gems/rake-%{rake_version}/lib

mkdir -p %{buildroot}%{gem_dir}/gems/rdoc-%{rdoc_version}/lib
mv %{buildroot}%{ruby_libdir}/rdoc* %{buildroot}%{gem_dir}/gems/rdoc-%{rdoc_version}/lib

mkdir -p %{buildroot}%{gem_dir}/gems/bigdecimal-%{bigdecimal_version}/lib
mkdir -p %{buildroot}%{gem_extdir}/bigdecimal-%{bigdecimal_version}/lib
mv %{buildroot}%{ruby_libdir}/bigdecimal %{buildroot}%{gem_dir}/gems/bigdecimal-%{bigdecimal_version}/lib
mv %{buildroot}%{ruby_libarchdir}/bigdecimal.so %{buildroot}%{gem_extdir}/bigdecimal-%{bigdecimal_version}/lib
ln -s %{gem_dir}/gems/bigdecimal-%{bigdecimal_version}/lib/bigdecimal %{buildroot}%{ruby_libdir}/bigdecimal
ln -s %{gem_extdir}/bigdecimal-%{bigdecimal_version}/lib/bigdecimal.so %{buildroot}%{ruby_libarchdir}/bigdecimal.so

mkdir -p %{buildroot}%{gem_dir}/gems/io-console-%{io_console_version}/lib
mkdir -p %{buildroot}%{gem_extdir}/io-console-%{io_console_version}/lib/io
mv %{buildroot}%{ruby_libdir}/io %{buildroot}%{gem_dir}/gems/io-console-%{io_console_version}/lib
mv %{buildroot}%{ruby_libarchdir}/io/console.so %{buildroot}%{gem_extdir}/io-console-%{io_console_version}/lib/io
ln -s %{gem_dir}/gems/io-console-%{io_console_version}/lib/io %{buildroot}%{ruby_libdir}/io
ln -s %{gem_extdir}/io-console-%{io_console_version}/lib/io/console.so %{buildroot}%{ruby_libarchdir}/io/console.so

mkdir -p %{buildroot}%{gem_dir}/gems/json-%{json_version}/lib
mkdir -p %{buildroot}%{gem_extdir}/json-%{json_version}/lib
mv %{buildroot}%{ruby_libdir}/json* %{buildroot}%{gem_dir}/gems/json-%{json_version}/lib
mv %{buildroot}%{ruby_libarchdir}/json/ %{buildroot}%{gem_extdir}/json-%{json_version}/lib/

mkdir -p %{buildroot}%{gem_dir}/gems/minitest-%{minitest_version}/lib
mv %{buildroot}%{ruby_libdir}/minitest %{buildroot}%{gem_dir}/gems/minitest-%{minitest_version}/lib

# Fix shebang to use this version
for i in $(find %{buildroot} -type f); do
    sed -i -re '1s|^#!/usr/bin/(env )?ruby.*|#!/usr/bin/env ruby%{base_dotver}|' $i
done

# Fix the shebang installed gems use
sed -i -re 's|shebang = "#!/usr/bin/ruby"|shebang = "#!/usr/bin/env ruby%{base_dotver}"|' \
    %{buildroot}%{rubygems_dir}/rubygems/installer_test_case.rb

# Adjust the gemspec files so that the gems will load properly
sed -i '2 a\
  s.require_paths = ["lib"]' %{buildroot}%{gem_dir}/specifications/rake-%{rake_version}.gemspec

sed -i '2 a\
  s.require_paths = ["lib"]' %{buildroot}%{gem_dir}/specifications/rdoc-%{rdoc_version}.gemspec

sed -i '2 a\
  s.require_paths = ["lib"]\
  s.extensions = ["bigdecimal.so"]' %{buildroot}%{gem_dir}/specifications/bigdecimal-%{bigdecimal_version}.gemspec

sed -i '2 a\
  s.require_paths = ["lib"]\
  s.extensions = ["io/console.so"]' %{buildroot}%{gem_dir}/specifications/io-console-%{io_console_version}.gemspec

sed -i '2 a\
  s.require_paths = ["lib"]\
  s.extensions = ["json/ext/parser.so", "json/ext/generator.so"]' %{buildroot}%{gem_dir}/specifications/json-%{json_version}.gemspec

sed -i '2 a\
  s.require_paths = ["lib"]' %{buildroot}%{gem_dir}/specifications/minitest-%{minitest_version}.gemspec

# Create ghost files for supported scripts
for b in ruby erb testrb ri irb rdoc; do
    touch %{buildroot}%{_bindir}/${b}
done

# Create ghost files for supported man pages
for m in ruby erb irb ri ; do
    # RPM compresses all man pages automatically so the ghost file must be "compressed"
    touch %{buildroot}%{_mandir}/man1/${m}.1.gz
done

# relocate the .so for the devel package
rm -f %{buildroot}%{_libdir}/libruby.so
ln -s ../../libruby.so.%{ruby_abi} %{buildroot}%{ruby_libarchdir}/libruby.so

# update pkgconfig
sed -i -r -e "s|^LIBPATH=.*|LIBPATH=%{ruby_libarchdir}|" \
    -e "s|^libdir=.*|libdir=%{ruby_libarchdir}|" \
    -e "s|^includedir=.*|includedir=%{_includedir}/%{base_name}%{base_dotver}|" \
    %{buildroot}%{_libdir}/pkgconfig/ruby-%{base_dotver}.pc
ln -s ruby-%{base_dotver}.pc %{buildroot}%{_libdir}/pkgconfig/ruby%{base_dotver}.pc

# Create ghost pkgconfig file
touch %{buildroot}/%{_libdir}/pkgconfig/ruby.pc

# fix the path to libruby.so
#   CONFIG["LIBRUBYARG"] = "-L$(archdir) $(LIBRUBYARG_SHARED)"
sed -i -e 's/$(LIBRUBYARG_SHARED)/-L$(archdir) $(LIBRUBYARG_SHARED)/g' %{buildroot}%{ruby_libarchdir}/rbconfig.rb

# we package these doc files as part of the -doc subpackage
rm -rf %{buildroot}%{_datadir}/doc/%{base_name}

# this is a compat module setup that older versions of ruby19 didn't use to
# ship - don't start now. (RDocTask -> RDoc:Task)
rm -rf %{buildroot}%{_datadir}/ri/%{base_dotver}/system/RDocTask

%check
DISABLE_TESTS=""

# OpenSSL 1.0.1 is breaking the drb test suite.
# https://bugs.ruby-lang.org/issues/6221
#DISABLE_TESTS="-x test_drbssl.rb $DISABLE_TESTS"

%ifarch armv7l armv7hl armv7hnl
# test_call_double(DL::TestDL) fails on ARM HardFP
# http://bugs.ruby-lang.org/issues/6592
DISABLE_TESTS="-x test_dl2.rb $DISABLE_TESTS"
%endif

%ifarch %{arm}
# test_parse.rb fails on ARM at line 787
# http://bugs.ruby-lang.org/issues/6899
DISABLE_TESTS="-x test_parse.rb $DISABLE_TESTS"
%endif

%ifnarch ppc ppc64
make check TESTS="-v $DISABLE_TESTS"
%endif

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%post
%{_sbindir}/update-alternatives \
  --install %{_bindir}/ruby              ruby    %{_bindir}/ruby%{base_dotver} %{priority} \
  --slave   %{_bindir}/erb               erb     %{_bindir}/erb%{base_dotver} \
  --slave   %{_bindir}/testrb            testrb  %{_bindir}/testrb%{base_dotver} \
  --slave   %{_bindir}/ri                ri      %{_bindir}/ri%{base_dotver} \
  --slave   %{_bindir}/irb               irb     %{_bindir}/irb%{base_dotver} \
  --slave   %{_bindir}/rdoc              rdoc    %{_bindir}/rdoc%{base_dotver} \
  --slave   %{_bindir}/gem               gem     %{_bindir}/gem%{base_dotver} \
  --slave   %{_mandir}/man1/ruby.1.gz    ruby.1  %{_mandir}/man1/ruby%{base_dotver}.1.gz \
  --slave   %{_mandir}/man1/erb.1.gz     erb.1   %{_mandir}/man1/erb%{base_dotver}.1.gz \
  --slave   %{_mandir}/man1/irb.1.gz     irb.1   %{_mandir}/man1/irb%{base_dotver}.1.gz \
  --slave   %{_mandir}/man1/ri.1.gz      ri.1    %{_mandir}/man1/ri%{base_dotver}.1.gz \
  --slave   %{_libdir}/pkgconfig/ruby.pc ruby.pc %{_libdir}/pkgconfig/ruby%{base_dotver}.pc

%preun
if [ $1 -eq 0 ]; then
    %{_sbindir}/update-alternatives --remove ruby %{_bindir}/ruby%{base_dotver}
fi

%files
%doc COPYING
%lang(ja) %doc COPYING.ja
%doc GPL
%doc LEGAL
%doc NEWS
%doc README
%lang(ja) %doc README.ja
%doc ToDo
%doc doc/ChangeLog-*
%doc doc/NEWS-*
%{_bindir}/erb%{base_dotver}
%{_bindir}/ruby%{base_dotver}
%{_bindir}/testrb%{base_dotver}
%ghost %{_bindir}/erb
%ghost %{_bindir}/ruby
%ghost %{_bindir}/testrb
%{_mandir}/man1/erb%{base_dotver}.1*
%{_mandir}/man1/ruby%{base_dotver}.1*
%ghost %{_mandir}/man1/erb.1*
%ghost %{_mandir}/man1/ruby.1*

# http://fedoraproject.org/wiki/Packaging:Guidelines#Packaging_Static_Libraries
%exclude %{_libdir}/libruby-static.a

%files devel
%doc COPYING*
%doc GPL
%doc LEGAL
%doc README.EXT
%lang(ja) %doc README.EXT.ja
%config(noreplace) %{_sysconfdir}/rpm/macros.%{name}
%{_includedir}/%{base_name}%{base_dotver}
%{ruby_libarchdir}/libruby.so
%{_libdir}/pkgconfig/ruby-%{base_dotver}.pc
%{_libdir}/pkgconfig/ruby%{base_dotver}.pc
%ghost %{_libdir}/pkgconfig/ruby.pc

# TODO
# ruby.pc still needs fixing, see bug 789532 comment 8

%files libs
%doc COPYING
%lang(ja) %doc COPYING.ja
%doc GPL
%doc LEGAL
%doc README
%lang(ja) %doc README.ja
%doc NEWS
%doc doc/NEWS-*
# Exclude /usr/local directory since it is supposed to be managed by
# local system administrator.
%exclude %{ruby_sitelibdir}
%exclude %{ruby_sitearchdir}
%{ruby_vendorlibdir}
%{ruby_vendorarchdir}

# List all these files explicitly to prevent surprises
# Platform independent libraries.
%dir %{ruby_libdir}
%{ruby_libdir}/*.rb
%if %{with X11}
%exclude %{ruby_libdir}/*-tk.rb
%exclude %{ruby_libdir}/irb.rb
%exclude %{ruby_libdir}/tcltk.rb
%exclude %{ruby_libdir}/tk*.rb
%endif
%{ruby_libdir}/cgi
%{ruby_libdir}/date
%{ruby_libdir}/digest
%{ruby_libdir}/dl
%{ruby_libdir}/drb
%if 0%{?rhel} > 5 || 0%{?amzn}
%{ruby_libdir}/fiddle
%endif
%exclude %{ruby_libdir}/irb
%{ruby_libdir}/matrix
%{ruby_libdir}/net
%{ruby_libdir}/openssl
%{ruby_libdir}/optparse
%{ruby_libdir}/psych
%{ruby_libdir}/racc
%{ruby_libdir}/rbconfig
%{ruby_libdir}/rexml
%{ruby_libdir}/rinda
%{ruby_libdir}/ripper
%{ruby_libdir}/rss
%{ruby_libdir}/shell
%{ruby_libdir}/syck
%{ruby_libdir}/test
%if %{with X11}
%exclude %{ruby_libdir}/tk
%exclude %{ruby_libdir}/tkextlib
%endif
%{ruby_libdir}/uri
%{ruby_libdir}/webrick
%{ruby_libdir}/xmlrpc
%{ruby_libdir}/yaml

# Platform specific libraries.
%{_libdir}/libruby.so.*
%dir %{ruby_libarchdir}
%{ruby_libarchdir}/continuation.so
%{ruby_libarchdir}/coverage.so
%{ruby_libarchdir}/curses.so
%{ruby_libarchdir}/date_core.so
%{ruby_libarchdir}/dbm.so
%dir %{ruby_libarchdir}/digest
%{ruby_libarchdir}/digest.so
%{ruby_libarchdir}/digest/bubblebabble.so
%{ruby_libarchdir}/digest/md5.so
%{ruby_libarchdir}/digest/rmd160.so
%{ruby_libarchdir}/digest/sha1.so
%{ruby_libarchdir}/digest/sha2.so
%dir %{ruby_libarchdir}/dl
%{ruby_libarchdir}/dl.so
%{ruby_libarchdir}/dl/callback.so
%dir %{ruby_libarchdir}/enc
%{ruby_libarchdir}/enc/big5.so
%{ruby_libarchdir}/enc/cp949.so
%{ruby_libarchdir}/enc/emacs_mule.so
%{ruby_libarchdir}/enc/encdb.so
%{ruby_libarchdir}/enc/euc_jp.so
%{ruby_libarchdir}/enc/euc_kr.so
%{ruby_libarchdir}/enc/euc_tw.so
%{ruby_libarchdir}/enc/gb18030.so
%{ruby_libarchdir}/enc/gb2312.so
%{ruby_libarchdir}/enc/gbk.so
%{ruby_libarchdir}/enc/iso_8859_1.so
%{ruby_libarchdir}/enc/iso_8859_10.so
%{ruby_libarchdir}/enc/iso_8859_11.so
%{ruby_libarchdir}/enc/iso_8859_13.so
%{ruby_libarchdir}/enc/iso_8859_14.so
%{ruby_libarchdir}/enc/iso_8859_15.so
%{ruby_libarchdir}/enc/iso_8859_16.so
%{ruby_libarchdir}/enc/iso_8859_2.so
%{ruby_libarchdir}/enc/iso_8859_3.so
%{ruby_libarchdir}/enc/iso_8859_4.so
%{ruby_libarchdir}/enc/iso_8859_5.so
%{ruby_libarchdir}/enc/iso_8859_6.so
%{ruby_libarchdir}/enc/iso_8859_7.so
%{ruby_libarchdir}/enc/iso_8859_8.so
%{ruby_libarchdir}/enc/iso_8859_9.so
%{ruby_libarchdir}/enc/koi8_r.so
%{ruby_libarchdir}/enc/koi8_u.so
%{ruby_libarchdir}/enc/shift_jis.so
%dir %{ruby_libarchdir}/enc/trans
%{ruby_libarchdir}/enc/trans/big5.so
%{ruby_libarchdir}/enc/trans/chinese.so
%{ruby_libarchdir}/enc/trans/emoji.so
%{ruby_libarchdir}/enc/trans/emoji_iso2022_kddi.so
%{ruby_libarchdir}/enc/trans/emoji_sjis_docomo.so
%{ruby_libarchdir}/enc/trans/emoji_sjis_kddi.so
%{ruby_libarchdir}/enc/trans/emoji_sjis_softbank.so
%{ruby_libarchdir}/enc/trans/escape.so
%{ruby_libarchdir}/enc/trans/gb18030.so
%{ruby_libarchdir}/enc/trans/gbk.so
%{ruby_libarchdir}/enc/trans/iso2022.so
%{ruby_libarchdir}/enc/trans/japanese.so
%{ruby_libarchdir}/enc/trans/japanese_euc.so
%{ruby_libarchdir}/enc/trans/japanese_sjis.so
%{ruby_libarchdir}/enc/trans/korean.so
%{ruby_libarchdir}/enc/trans/single_byte.so
%{ruby_libarchdir}/enc/trans/transdb.so
%{ruby_libarchdir}/enc/trans/utf8_mac.so
%{ruby_libarchdir}/enc/trans/utf_16_32.so
%{ruby_libarchdir}/enc/utf_16be.so
%{ruby_libarchdir}/enc/utf_16le.so
%{ruby_libarchdir}/enc/utf_32be.so
%{ruby_libarchdir}/enc/utf_32le.so
%{ruby_libarchdir}/enc/windows_1251.so
%{ruby_libarchdir}/etc.so
%{ruby_libarchdir}/fcntl.so
%{ruby_libarchdir}/fiber.so
%if 0%{?rhel} > 5 || 0%{?amzn}
%{ruby_libarchdir}/fiddle.so
%endif
%{ruby_libarchdir}/gdbm.so
%{ruby_libarchdir}/iconv.so
%dir %{ruby_libarchdir}/io
%{ruby_libarchdir}/io/nonblock.so
%{ruby_libarchdir}/io/wait.so
%dir %{ruby_libarchdir}/mathn
%{ruby_libarchdir}/mathn/complex.so
%{ruby_libarchdir}/mathn/rational.so
%{ruby_libarchdir}/nkf.so
%{ruby_libarchdir}/objspace.so
%{ruby_libarchdir}/openssl.so
%{ruby_libarchdir}/pathname.so
%{ruby_libarchdir}/psych.so
%{ruby_libarchdir}/pty.so
%dir %{ruby_libarchdir}/racc
%{ruby_libarchdir}/racc/cparse.so
%{ruby_libarchdir}/rbconfig.rb
%{ruby_libarchdir}/readline.so
%{ruby_libarchdir}/ripper.so
%{ruby_libarchdir}/sdbm.so
%{ruby_libarchdir}/socket.so
%{ruby_libarchdir}/stringio.so
%{ruby_libarchdir}/strscan.so
%{ruby_libarchdir}/syck.so
%{ruby_libarchdir}/syslog.so
%if %{with X11}
%exclude %{ruby_libarchdir}/tcltklib.so
%exclude %{ruby_libarchdir}/tkutil.so
%endif
%{ruby_libarchdir}/zlib.so

%files -n rubygems%{base_ver}
%{_bindir}/gem%{base_dotver}
%{rubygems_dir}
%exclude %{gem_dir}/gems/*
%dir %{_libdir}/gems%{base_dotver}
%dir %{_exec_prefix}/lib*/gems%{base_dotver}
%dir %{_exec_prefix}/lib*/gems%{base_dotver}/exts
%exclude %{gem_extdir}/bigdecimal-%{bigdecimal_version}
%exclude %{gem_extdir}/io-console-%{io_console_version}
%exclude %{gem_extdir}/json-%{json_version}
%exclude %{gem_dir}/gems/rake-%{rake_version}
%exclude %{gem_dir}/gems/rdoc-%{rdoc_version}
%exclude %{gem_dir}/specifications/bigdecimal-%{bigdecimal_version}.gemspec
%exclude %{gem_dir}/specifications/io-console-%{io_console_version}.gemspec
%exclude %{gem_dir}/specifications/json-%{json_version}.gemspec
%exclude %{gem_dir}/specifications/minitest-%{minitest_version}.gemspec
%exclude %{gem_dir}/specifications/rake-%{rake_version}.gemspec
%exclude %{gem_dir}/specifications/rdoc-%{rdoc_version}.gemspec

%files -n rubygems%{base_ver}-devel
%config(noreplace) %{_sysconfdir}/rpm/macros.%{name}gems

%files -n rubygem%{base_ver}-rake
%{_bindir}/rake%{base_dotver}
%{gem_dir}/gems/rake-%{rake_version}
%{gem_dir}/specifications/rake-%{rake_version}.gemspec
%{_mandir}/man1/rake*

%files irb
%{_bindir}/irb%{base_dotver}
%ghost %{_bindir}/irb
%{ruby_libdir}/irb.rb
%{ruby_libdir}/irb
%{_mandir}/man1/irb%{base_dotver}.1*
%ghost %{_mandir}/man1/irb.1*

%files -n rubygem%{base_ver}-rdoc
%{_bindir}/rdoc%{base_dotver}
%{_bindir}/ri%{base_dotver}
%ghost %{_bindir}/rdoc
%ghost %{_bindir}/ri
%{gem_dir}/gems/rdoc-%{rdoc_version}
%{gem_dir}/specifications/rdoc-%{rdoc_version}.gemspec
%{_mandir}/man1/ri%{base_dotver}.1*
%ghost %{_mandir}/man1/ri.1*
%{_datadir}/ri/%{base_dotver}

%files doc
%doc README
%lang(ja) %doc README.ja
%doc ChangeLog
%doc doc/ChangeLog-*
%doc doc/capi/html

%files -n rubygem%{base_ver}-bigdecimal
%{gem_extdir}/bigdecimal-%{bigdecimal_version}
%{gem_dir}/gems/bigdecimal-%{bigdecimal_version}
%{gem_dir}/specifications/bigdecimal-%{bigdecimal_version}.gemspec
%{ruby_libdir}/bigdecimal
%{ruby_libarchdir}/bigdecimal.so

%files -n rubygem%{base_ver}-io-console
%{gem_extdir}/io-console-%{io_console_version}
%{gem_dir}/gems/io-console-%{io_console_version}
%{gem_dir}/specifications/io-console-%{io_console_version}.gemspec
%{ruby_libdir}/io
%{ruby_libarchdir}/io/console.so

%files -n rubygem%{base_ver}-json
%{gem_extdir}/json-%{json_version}
%{gem_dir}/gems/json-%{json_version}
%{gem_dir}/specifications/json-%{json_version}.gemspec

%files -n rubygem%{base_ver}-minitest
%{gem_dir}/gems/minitest-%{minitest_version}
%{gem_dir}/specifications/minitest-%{minitest_version}.gemspec

%if %{with X11}
%files tcltk
%{ruby_libdir}/*-tk.rb
%{ruby_libdir}/tcltk.rb
%{ruby_libdir}/tk*.rb
%{ruby_libarchdir}/tcltklib.so
%{ruby_libarchdir}/tkutil.so
%{ruby_libdir}/tk
%{ruby_libdir}/tkextlib
%endif

%changelog
* Tue Sep 24 2013 Lee Trager <ltrager@amazon.com>
- Add missing provides to rubygems19
- Add patch for CVE-2013-4287

* Fri Sep 20 2013 Lee Trager <ltrager@amazon.com>
- Add versioned provides

* Thu Sep 19 2013 Tom Kirchner <tjk@amazon.com>
- Fix shebangs changed by --program-suffix

* Thu Sep 19 2013 Lee Trager <ltrager@amazon.com>
- Don't rename libruby

* Wed Sep 18 2013 Lee Trager <ltrager@amazon.com>
- Use config script to rename everything

* Fri Sep 6 2013 Lee Trager <ltrager@amazon.com>
- Add alternatives support, cleanup spec file, add stricter requirements

* Tue Jul 16 2013 cyler <cyler@amazon.com>
- import source package F18/ruby-1.9.3.448-31.fc18

* Mon Jul  1 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.448-31
- Update to 1.9.3 p448
- Fix hostname check bypassing vulnerability in SSL client
  (CVE-2013-4073)

* Sat May 25 2013 cyler <cyler@amazon.com>
- make Provides: and Requires: versioned within the spec file

* Thu May 16 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.429-30
- Update to 1.9.3 p429
- Fix object taint bypassing in DL and Fiddle (CVE-2013-2065)

* Wed May 15 2013 cyler <cyler@amazon.com>
- require only a versioned ri binary
- fix intermittent rpmbuild %check failure in test_timeout.rb

* Thu May 9 2013 cyler <cyler@amazon.com>
- apply patches from rdoc's github issue #71 to fix occasional build error

* Tue May 7 2013 cyler <cyler@amazon.com>
- remove ruby19.pc per bcressey@/tjk@

* Mon May 6 2013 cyler <cyler@amazon.com>
- fix build error ruby-1.9.pc: No such file or directory
- import source package F17/ruby-1.9.3.392-29.fc17

* Mon Feb 25 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.392-29
- Update to 1.9.3 p392
- Fix entity expansion DoS vulnerability in REXML (bug 914716)

* Mon Feb 11 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.385-28
- Update to 1.9.3 p385

* Sat Jan 19 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.374-27
- Update to 1.9.3 p374
- Fix provided variables in pkgconfig (bug 789532:
  Vít Ondruch <vondruch@redhat.com>)

* Fri Jan 18 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.362-26
- Provide non-versioned pkgconfig file (bug 789532)
- Use db5 on F-19 (bug 894022)

* Wed Jan 16 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.362-25
- Backport fix for the upstream PR7629, save the proc made from the given block
  (bug 895173)

* Wed Jan  2 2013 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.362-24
- Update to 1.9.3.362

* Mon Dec 03 2012 Jaromir Capik <jcapik@redhat.com> - 1.9.3.327-23
- Skipping test_parse.rb (fails on ARM at line 787)
- http://bugs.ruby-lang.org/issues/6899

* Sun Nov 11 2012 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.327-23
- Skip test_str_crypt (on rawhide) for now (upstream bug 7312)

* Sat Nov 10 2012 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.327-22
- Ignore some network related tests

* Sat Nov 10 2012 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.327-21
- Update to 1.9.3.327
- Fix Hash-flooding DoS vulnerability on MurmurHash function
  (CVE-2012-5371)

* Mon Oct 22 2012 Cristian Gafton <gafton@amazon.com>
- keep the ri documenttaion in the rubygems-rdoc subpackage

* Fri Oct 19 2012 Cristian Gafton <gafton@amazon.com>
- disable parallel make in order to get deterministic compiler output.
- add doxygen to buildrequires
- don't package rdoctask alias for rdoc:task
- conditionalize noarch build for ruby-doc
- keep ssl tests enabled
- include the capi docs

* Wed Oct 17 2012 Lee Trager <ltrager@amazon.com>
- Fix bigdecimal ext gem path
- import source package F17/ruby-1.9.3.286-18.fc17

* Sat Oct 13 2012 Mamoru TASAKA <mtasaka@fedoraproject.org> - 1.9.3.286-19
- Update to 1.9.3 p286
- Don't create files when NUL-containing path name is passed
  (bug 865940, CVE-2012-4522)

* Thu Oct 04 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.9.3.194-18
- Patch from trunk for CVE-2012-4464, CVE-2012-4466

* Tue Oct 2 2012 Lee Trager <ltrager@amazon.com>
- import source package F17/ruby-1.9.3.194-16.fc17

* Mon Sep 24 2012 Lee Trager <ltrager@amazon.com>
- Rename RPM Macro files to macros.%{name}

* Thu Sep 06 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.194-17
- Split documentation into -doc subpackage (rhbz#854418).

* Tue Aug 14 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.194-16
- Revert the dependency of ruby-libs on rubygems (rhbz#845011, rhbz#847482).

* Wed Aug 01 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.194-15
- ruby-libs must require rubygems (rhbz#845011).

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.3.194-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jun 11 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.9.3.194-13
- Make the bigdecimal gem a runtime dependency of Ruby.

* Mon Jun 11 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.9.3.194-12
- Make symlinks for bigdecimal and io-console gems to ruby stdlib dirs (RHBZ 829209).

* Tue May 29 2012 Bohuslav Kabrda <bkabrda@redhat.com> - 1.9.3.194-11
- Fix license to contain Public Domain.
- macros.ruby now contains unexpanded macros.

* Sun Apr 22 2012 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.9.3.194-10.1
- Bump release

* Fri Apr 20 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.194-1
- Update to Ruby 1.9.3-p194.

* Mon Apr 09 2012 Karsten Hopp <karsten@redhat.com> 1.9.3.125-3
- disable check on ppc(64), RH bugzilla 803698

* Thu Mar 29 2012 Cristian Gafton <gafton@amazon.com>
- fix more embedded paths to point to ruby1.9 location
- update rbconfig to point to the proper location of libruby
- fix libruby symlink in the devel package
- fix interpreter paths for build as a secondary interpreter

* Wed Mar 7 2012 Cristian Gafton <gafton@amazon.com>
- syncronize versioned paths with the layout of ruby 1.8

* Thu Mar 1 2012 Cristian Gafton <gafton@amazon.com>
- run webrick tests independently first for a more predictible behavior
- allow building in older environments too (like el5-based ones)

* Wed Feb 29 2012 Peter Robinson <pbrobinson@fedoraproject.org> - 1.9.3.125-2
- Temporarily disable make check on ARM until it's fixed upstream. Tracked in RHBZ 789410

* Mon Feb 20 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.125-1
- Upgrade to Ruby 1.9.3-p125.

* Mon Feb 20 2012 Cristian Gafton <gafton@amazon.com>
- name-version the builtin rubygems packages after the ruby abi version

* Thu Feb 16 2012 Cristian Gafton <gafton@amazon.com>
- fix rpm macro definitions as installed when building as non-main ruby
- sync file manifest for noarch packages built on either 32 or 64 bit arches
- build it as a secondary interpreter ruby19
- add patch for test_udp_server check

* Fri Feb 10 2012 Nathan Blackham <blackham@amazon.com>
- Conditionalize X11 support
- Spec file cleanup

* Fri Feb 3 2012 Nathan Blackham <blackham@amazon.com>
- import source package F17/ruby-1.9.3.0-7.fc17

* Sun Jan 29 2012 Mamoru Tasaka <mtasaka@fedoraprpject.org> - 1.9.3.0-7
- Make mkmf.rb verbose by default

* Thu Jan 26 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.0-6
- Relax dependencies to allow external updates of bundled gems.

* Wed Jan 18 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.0-5
- Initial release of Ruby 1.9.3.
- Add rubygems dependency on io-console for user interactions.
- Gems license clarification.

* Tue Jan 17 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.0-4
- Bundled gems moved into dedicated directories and subpackages.
- Create and own RubyGems directories for binary extensions.
- Fix build with GCC 4.7.

* Mon Jan 16 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.0-3
- Fix RHEL build.
- Fixed directory ownership.
- Verose build output.

* Sun Jan 15 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.0-2
- Install RubyGems outside of Ruby directory structure.
- RubyGems has not its own -devel subpackage.
- Enhanced macros.ruby and macros.rubygems.
- All tests are green now (bkabrda).

* Sat Jan 14 2012 Vít Ondruch <vondruch@redhat.com> - 1.9.3.0-1
- Initial package

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.7.357-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Thu Dec 29 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.7.357-1
- Update to 1.8.7p357
- Randomize hash on process startup (CVE-2011-4815, bug 750564)

* Fri Dec 23 2011 Dennis Gilmore <dennis@ausil.us> - 1.8.7.352-2
- dont normalise arm cpus to arm
- there is something weird about how ruby choses where to put bits

* Thu Nov 17 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.7.352-3
- F-17: kill gdbm support for now due to licensing compatibility issue

* Sat Oct  1 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.7.352-2
- F-17: rebuild against new gdbm

* Sat Jul 16 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.7.352-1
- Update to 1.8.7 p352
- CVE-2011-2686 is fixed in this version (bug 722415)
- Update ext/tk to the latest git
- Remove duplicate path entry (bug 718695)

* Thu Jul 14 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.7.334-4
- Once fix FTBFS (bug 716021)

* Mon Jul 11 2011 Dennis Gilmore <dennis@ausil.us> - 1.8.7.334-3
- normalise arm cpus to arm

* Mon May 30 2011 Mamoru Tasaka <mtasaka@fedoraproject.org> - 1.8.7.334-2
- Own %%{_normalized_cpu}-%%{_target_os} directory (bug 708816)

* Sat Feb 19 2011 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.7.334-1
- Update to 1.8.7 p334

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.8.7.330-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Jan 02 2011 Dennis Gilmore <dennis@ausil.us> - 1.8.7.330-2
- nomalise the 32 bit sparc archs to sparc

* Sun Dec 26 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.7.330-1
- Update to 1.8.7 p330
- ext/tk updated to the newest header

* Thu Nov  4 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.7.302-2
- Avoid multilib conflict on -libs subpackage (bug 649174)

* Mon Aug 23 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.7.302-1
- Update to 1.8.7.302
- CVE-2010-0541 (bug 587731) is fixed in this version
- Update ext/tk to the latest head

* Mon Aug  2 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.7.299-5
- More cleanup of spec file, expecially for rpmlint issue
- build ri files in %%build

* Mon Jul 26 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.7.299-4
- Cleanup spec file
- Make -irb, -rdoc subpackage noarch
- Make dependencies between arch-dependent subpackages isa specific
- Improve sample documentation gathering

* Mon Jul 12 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.299-3
- updated packaged based on feedback (from mtasaka)
- added comments to all patches / sources
- obsoleted ruby-mode, as it's now provided by the emacs package itself
- readded missing documentation
- various small compatability/regression fixes

* Tue Jul 06 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.299-2
- readded bits to pull tk package from upstream source branch
- removed unecessary .tk.old dir
- renamed macros which may cause confusion, removed unused ones

* Thu Jun 24 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.299-1
- integrate more of jmeyering's and mtaska's feedback
- removed emacs bits that are now shipped with the emacs package
- various patch and spec cleanup
- rebased to ruby 1.8.7 patch 299, removed patches no longer needed:
   ruby-1.8.7-openssl-1.0.patch, ruby-1.8.7-rb_gc_guard_ptr-optimization.patch

* Wed Jun 23 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.249-5
- Various fixes

* Wed Jun 23 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.249-4
- Fixed incorrect paths in 1.8.7 rpm

* Tue Jun 22 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.249-3
- Integrated Jim Meyering's feedback and changes in to:
- remove trailing blanks
- placate rpmlint
- ruby_* definitions: do not use trailing slashes in directory names
- _normalized_cpu: simplify definition

* Mon Jun 21 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.249-2
- Integrate mtasaka's feedback and changes
- patch101 ruby_1_8_7-rb_gc_guard_ptr-optimization.patch

* Tue Jun 15 2010 Mohammed Morsi <mmorsi@redhat.com> - 1.8.7.249-1
- Initial Ruby 1.8.7 specfile

* Wed May 19 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.399-5
- Retry for bug 559158, Simplify the OpenSSL::Digest class
  pull more change commits from ruby_1_8 branch

* Mon May 17 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.399-4
- Patch36 (ruby-1.8.x-RHASH_SIZE-rb_hash_lookup-def.patch)
  also backport rb_hash_lookup definition (bug 592936)

* Thu May 13 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.399-3
- ruby-1.8.x-null-class-must-be-Qnil.patch (bug 530407)
- Recreate some patches using upstream svn when available, and
  add some comments for patches

* Tue May 11 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.399-2
- tcltk: Give up using potentially unmaintained ruby_1_8_6 branch
  and instead completely replace with ruby_1_8 branch head
  (at this time, using rev 27738)
  (seems to fix 560053, 590503)
- Fix Japanese encoding strings under ruby-tcltk/ext/tk/sample/

* Tue Apr 27 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.399-1
- Update to 1.8.6 p 399 (bug 579675)
- Patch to fix gc bug causing open4 crash (bug 580993)

* Fri Mar 12 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.388-9
- F-14: rebuild against new gdbm

* Thu Jan 28 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp>
- Once revert the previous change (patch34)

* Wed Jan 27 2010 Jeroen van Meeuwen <j.van.meeuwen@ogd.nl> - 1.8.6.388-8
- Backport openssl/digest functions providing digest and hexdigest functions
  directly in OpenSSL::Digest.methods
- Make sure that Red Hat people version their changelog entries
- This is actually release #1, but now needs to be release #7

* Mon Jan 18 2010 Akira TAGOH <tagoh@redhat.com> - 1.8.6.388-1
- Add conditional for RHEL.

* Wed Jan 13 2010 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.383-6
- CVE-2009-4492 ruby WEBrick log escape sequence (bug 554485)

* Wed Dec  9 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.383-5
- Change mkmf.rb to use LIBRUBYARG_SHARED so that have_library() works
  without libruby-static.a (bug 428384)
- And move libruby-static.a to -static subpackage

* Thu Oct 29 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.383-4
- Use bison to regenerate parse.c to keep the original format of error
  messages (bug 530275 comment 4)

* Sun Oct 25 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.383-3
- Patch so that irb saves its history (bug 518584, ruby issue 1556)

* Sat Oct 24 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.383-2
- Update to 1.8.6 patchlevel 383 (bug 520063)

* Wed Oct 14 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.369-5
- Much better idea for Patch31 provided by Akira TAGOH <tagoh@redhat.com>

* Wed Oct 14 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.369-4
- Fix the search path of ri command for ri manuals installed with gem
  (bug 528787)

* Wed Aug 26 2009 Tomas Mraz <tmraz@redhat.com> - 1.8.6.369-3
- Rebuild against new openssl

* Thu Jul 23 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.369-2
- Make sure that readline.so is linked against readline 5 because
  Ruby is under GPLv2

* Sat Jun 20 2009 Jeroen van Meeuwen <kanarip@fedoraproject.org> - 1.8.6.369-1
- New patchlevel fixing CVE-2009-1904
- Fix directory on ARM (#506233, Kedar Sovani)

* Sun May 31 2009 Jeroen van Meeuwen <j.van.meeuwen@ogd.nl> - 1.8.6.368-1
- New upstream release (p368)

* Sat Apr 11 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.287-8
- Merge Review fix (#226381)

* Wed Mar 18 2009 Jeroen van Meeuwen <j.van.meeuwen@ogd.nl> - 1.8.6.287-7
- Fix regression in CVE-2008-3790 (#485383)

* Mon Mar 16 2009 Mamoru Tasaka <mtasaka@ioa.s.u-tokyo.ac.jp> - 1.8.6.287-6
- Again use -O2 optimization level
- i586 should search i386-linux directory (on <= F-11)

* Thu Mar 05 2009 Jeroen van Meeuwen <kanarip@fedoraproject.org> - 1.8.6.287-5
- Rebuild for gcc4.4

* Fri Feb 27 2009 Jeroen van Meeuwen <kanarip@fedoraproject.org> - 1.8.6.287-3
- CVE-2008-5189: CGI header injection.

* Wed Oct  8 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.287-2
- CVE-2008-3790: DoS vulnerability in the REXML module.

* Sat Aug 23 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.287-1
- New upstream release.
- Security fixes.
  - CVE-2008-3655: Ruby does not properly restrict access to critical
                   variables and methods at various safe levels.
  - CVE-2008-3656: DoS vulnerability in WEBrick.
  - CVE-2008-3657: Lack of taintness check in dl.
  - CVE-2008-1447: DNS spoofing vulnerability in resolv.rb.
  - CVE-2008-3443: Memory allocation failure in Ruby regex engine.
- Remove the unnecessary backported patches.

* Thu Jul 10 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1.8.6.230-5
- rebuild against db4-4.7

* Tue Jul  1 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.230-4
- Backported from upstream SVN to fix a segfault issue with Array#fill.

* Mon Jun 30 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.230-3
- Backported from upstream SVN to fix a segfault issue. (#452825)
- Backported from upstream SVN to fix an integer overflow in rb_ary_fill.

* Wed Jun 25 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.230-2
- Fix a segfault issue. (#452810)

* Tue Jun 24 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.230-1
- New upstream release.
- Security fixes. (#452295)
  - CVE-2008-1891: WEBrick CGI source disclosure.
  - CVE-2008-2662: Integer overflow in rb_str_buf_append().
  - CVE-2008-2663: Integer overflow in rb_ary_store().
  - CVE-2008-2664: Unsafe use of alloca in rb_str_format().
  - CVE-2008-2725: Integer overflow in rb_ary_splice().
  - CVE-2008-2726: Integer overflow in rb_ary_splice().
- ruby-1.8.6.111-CVE-2007-5162.patch: removed.
- Build ruby-mode package for all archtectures.

* Tue Mar  4 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.114-1
- Security fix for CVE-2008-1145.
- Improve a spec file. (#226381)
  - Correct License tag.
  - Fix a timestamp issue.
  - Own a arch-specific directory.

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.8.6.111-9
- Autorebuild for GCC 4.3

* Tue Feb 19 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-8
- Rebuild for gcc-4.3.

* Tue Jan 15 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-7
- Revert the change of libruby-static.a. (#428384)

* Fri Jan 11 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-6
- Fix an unnecessary replacement for shebang. (#426835)

* Fri Jan  4 2008 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-5
- Rebuild.

* Fri Dec 28 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-4
- Clean up again.

* Fri Dec 21 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-3
- Clean up the spec file.
- Remove ruby-man-1.4.6 stuff. this is entirely the out-dated document.
  this could be replaced by ri.
- Disable the static library building.

* Tue Dec 04 2007 Release Engineering <rel-eng at fedoraproject dot org> - 1.8.6.111-2
- Rebuild for openssl bump

* Wed Oct 31 2007 Akira TAGOH <tagoh@redhat.com>
- Fix the dead link.

* Mon Oct 29 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.111-1
- New upstream release.
- ruby-1.8.6.111-CVE-2007-5162.patch: Update a bit with backporting the changes
   at trunk to enable the fix without any modifications on the users' scripts.
   Note that Net::HTTP#enable_post_connection_check isn't available anymore.
   If you want to disable this post-check, you should give OpenSSL::SSL::VERIFY_NONE
   to Net::HTTP#verify_mode= instead of.

* Mon Oct 15 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.110-2
- Enable pthread support for ppc too. (#201452)
- Fix unexpected dependencies appears in ruby-libs. (#253325)

* Wed Oct 10 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.110-1
- New upstream release.
  - ruby-r12567.patch: removed.
- ruby-1.8.6-CVE-2007-5162.patch: security fix for Net::HTTP that is
  insufficient verification of SSL certificate.

* Thu Aug 23 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.36-4
- Rebuild

* Fri Aug 10 2007 Akira TAGOH <tagoh@redhat.com>
- Update License tag.

* Mon Jun 25 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.36-3
- ruby-r12567.patch: backport patch from upstream svn to get rid of
  the unnecessary declarations. (#245446)

* Wed Jun 20 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6.36-2
- New upstream release.
  - Fix Etc::getgrgid to get the correct gid as requested. (#236647)

* Wed Mar 28 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6-2
- Fix search path breakage. (#234029)

* Thu Mar 15 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.6-1
- New upstream release.
- clean up a spec file.

* Tue Feb 13 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.5.12-2
- Rebuild

* Mon Feb  5 2007 Akira TAGOH <tagoh@redhat.com> - 1.8.5.12-1
- New upstream release.

* Mon Dec 11 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.5.2-1
- security fix release.

* Fri Oct 27 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.5-4
- security fix release.
- ruby-1.8.5-cgi-CVE-2006-5467.patch: fix a CGI multipart parsing bug that
  causes the denial of service. (#212396)

* Sun Oct 01 2006 Jesse Keating <jkeating@redhat.com> - 1.8.5-3
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Tue Sep 26 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.5-2
- fixed rbconfig.rb to refer to DESTDIR for sitearchdir. (#207311)

* Mon Aug 28 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.5-1
- New upstream release.
- removed the unnecessary patches:
  - ruby-1.8.4-no-eaccess.patch
  - ruby-1.8.4-64bit-pack.patch
  - ruby-1.8.4-fix-insecure-dir-operation.patch
  - ruby-1.8.4-fix-insecure-regexp-modification.patch
  - ruby-1.8.4-fix-alias-safe-level.patch
- build with --enable-pthread except on ppc.
- ruby-1.8.5-hash-memory-leak.patch: backported from CVS to fix a memory leak
  on Hash. [ruby-talk:211233]

* Mon Aug  7 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-12
- owns sitearchdir. (#201208)

* Thu Jul 20 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-11
- security fixes [CVE-2006-3694]
  - ruby-1.8.4-fix-insecure-dir-operation.patch:
  - ruby-1.8.4-fix-insecure-regexp-modification.patch: fixed the insecure
    operations in the certain safe-level restrictions. (#199538)
  - ruby-1.8.4-fix-alias-safe-level.patch: fixed to not bypass the certain
    safe-level restrictions. (#199543)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.8.4-10.fc6.1
- rebuild

* Mon Jun 19 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-10
- fixed the wrong file list again. moved tcltk library into ruby-tcltk.
  (#195872)

* Thu Jun  8 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-8
- ruby-deprecated-sitelib-search-path.patch: correct the order of search path.

* Wed Jun  7 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-7
- exclude ppc64 to make ruby-mode package. right now emacs.ppc64 isn't provided
  and buildsys became much stricter.
- ruby-deprecated-sitelib-search-path.patch: applied to add more search path
  for backward compatiblity.
- added byacc to BuildReq. (#194161)

* Wed May 17 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-6
- ruby-deprecated-search-path.patch: added the deprecated installation paths
  to the search path for the backward compatibility.
- added a Provides: ruby(abi) to ruby-libs.
- ruby-1.8.4-64bit-pack.patch: backport patch from upstream to fix unpack("l")
  not working on 64bit arch and integer overflow on template "w". (#189350)
- updated License tag to be more comfortable, and with a pointer to get more
  details, like Python package does. (#179933)
- clean up.

* Wed Apr 19 2006 Akira TAGOH <tagoh@redhat.com>
- ruby-rubyprefix.patch: moved all arch-independent modules under /usr/lib/ruby
  and keep arch-dependent modules under /usr/lib64/ruby for 64bit archs.
  so 'rubylibdir', 'sitelibdir' and 'sitedir' in Config::CONFIG points to
  the kind of /usr/lib/ruby now. (#184199)

* Mon Apr 17 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-4
- correct sitelibdir. (#184198)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 1.8.4-3.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 1.8.4-3.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Mon Feb  6 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-3
- ruby-1.8.4-no-eaccess.patch: backported from ruby CVS to avoid conflict
  between newer glibc. (#179835)

* Wed Jan  4 2006 Akira TAGOH <tagoh@redhat.com> - 1.8.4-2
- ruby-tcltk-multilib.patch: fixed a typo.

* Tue Dec 27 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.4-1
- New upstream release.
  - fixed a missing return statement. (#140833)
  - fixed an use of uninitialized variable. (#144890)

* Fri Dec 16 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.4-0.4.preview2
- updates to 1.8.4-preview2.
- renamed the packages to ruby-* (#175765)
  - irb  -> ruby-irb
  - rdoc -> ruby-rdoc
  - ri   -> ruby-ri
- added tcl-devel and tk-devel into BuildRequires.

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Nov 10 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.4-0.3.preview1
- rebuilt against the latest openssl.

* Tue Nov  1 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.4-0.2.preview1
- build-deps libX11-devel instead of xorg-x11-devel.

* Mon Oct 31 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.4-0.1.preview1
- New upstream release.
- ruby-1.8.2-strscan-memset.patch: removed because it's no longer needed.

* Tue Oct  4 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.3-4
- moved the documents from ruby-libs to ruby-docs, which contains the arch
  specific thing and to be multilib support. (#168826)

* Mon Oct  3 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.3-3
- fixed the wrong file list. the external library for tcl/tk was included
  in ruby-libs unexpectedly.

* Mon Sep 26 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.3-2
- ruby-multilib.patch: added another chunk for multilib. (#169127)

* Wed Sep 21 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.3-1
- New upstream release.
- Build-Requires xorg-x11-devel instead of XFree86-devel.
- ruby-multilib.patch: applied for only 64-bit archs.
- ruby-1.8.2-xmlrpc-CAN-2005-1992.patch: removed. it has already been in upstream.

* Tue Jun 21 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-9
- ruby-1.8.2-xmlrpc-CAN-2005-1992.patch: fixed the arbitrary command execution
  on XMLRPC server. (#161096)

* Thu Jun 16 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-8
- ruby-1.8.2-tcltk-multilib.patch: applied to get tcltklib.so built. (#160194)

* Thu Apr  7 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-7
- ruby-1.8.2-deadcode.patch: removed the dead code from the source. (#146108)
- make sure that all documentation files in ruby-docs are the world-
  readable. (#147279)

* Tue Mar 22 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-6
- ruby-1.8.2-strscan-memset.patch: fixed an wrong usage of memset(3).

* Tue Mar 15 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-5
- rebuilt

* Tue Jan 25 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-4
- fixed the wrong generation of file manifest. (#146055)
- spec file clean up.

* Mon Jan 24 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-3
- separated out to rdoc package.
- make the dependency of irb for rdoc. (#144708)

* Wed Jan 12 2005 Tim Waugh <twaugh@redhat.com> - 1.8.2-2
- Rebuilt for new readline.

* Wed Jan  5 2005 Akira TAGOH <tagoh@redhat.com> - 1.8.2-1
- New upstream release.
- ruby-1.8.1-ia64-stack-limit.patch: removed - it's no longer needed.
- ruby-1.8.1-cgi_session_perms.patch: likewise.
- ruby-1.8.1-cgi-dos.patch: likewise.
- generated Ruby interactive documentation - senarated package.
  it's now provided as ri package. (#141806)

* Thu Nov 11 2004 Jeff Johnson <jbj@jbj.org> 1.8.1-10
- rebuild against db-4.3.21.

* Wed Nov 10 2004 Akira TAGOH <tagoh@redhat.com> - 1.8.1-9
- ruby-1.8.1-cgi-dos.patch: security fix [CAN-2004-0983]
- ruby-1.8.1-cgi_session_perms.patch: security fix [CAN-2004-0755]

* Fri Oct 29 2004 Akira TAGOH <tagoh@redhat.com> - 1.8.1-8
- added openssl-devel and db4-devel into BuildRequires (#137479)

* Wed Oct  6 2004 Akira TAGOH <tagoh@redhat.com> - 1.8.1-7
- require emacs-common instead of emacs.

* Wed Jun 23 2004 Akira TAGOH <tagoh@redhat.com> 1.8.1-4
- updated the documentation.

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Feb 04 2004 Akira TAGOH <tagoh@redhat.com> 1.8.1-1
- New upstream release.
- don't use any optimization for ia64 to avoid the build failure.
- ruby-1.8.1-ia64-stack-limit.patch: applied to fix SystemStackError when the optimization is disabled.

* Sat Dec 13 2003 Jeff Johnson <jbj@jbj.org> 1.8.0-3
- rebuild against db-4.2.52.

* Thu Sep 25 2003 Jeff Johnson <jbj@jbj.org> 1.8.0-2
- rebuild against db-4.2.42.

* Tue Aug  5 2003 Akira TAGOH <tagoh@redhat.com> 1.8.0-1
- New upstream release.

* Thu Jul 24 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-9.1
- rebuilt

* Thu Jul 24 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-9
- ruby-1.6.8-castnode.patch: handling the nodes with correct cast.
  use this patch now instead of ruby-1.6.8-fix-x86_64.patch.

* Fri Jul 04 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-8
- rebuilt

* Fri Jul 04 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-7
- fix the gcc warnings. (#82192)
- ruby-1.6.8-fix-x86_64.patch: correct a patch.
  NOTE: DON'T USE THIS PATCH FOR BIG ENDIAN ARCHITECTURE.
- ruby-1.6.7-long2int.patch: removed.

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb  7 2003 Jens Petersen <petersen@redhat.com> - 1.6.8-5
- rebuild against ucs4 tcltk

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Wed Jan 22 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-3
- ruby-1.6.8-multilib.patch: applied to fix the search path issue on x86_64

* Tue Jan 21 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-2
- ruby-1.6.8-require.patch: applied to fix the search bug in require.
- don't apply long2int patch to s390 and s390x. it doesn't work.

* Wed Jan 15 2003 Akira TAGOH <tagoh@redhat.com> 1.6.8-1
- New upstream release.
- removed some patches. it's no longer needed.
  - ruby-1.6.7-100.patch
  - ruby-1.6.7-101.patch
  - ruby-1.6.7-102.patch
  - ruby-1.6.7-103.patch
  - 801_extmk.rb-shellwords.patch
  - 801_mkmf.rb-shellwords.patch
  - 804_parse.y-new-bison.patch
  - 805_uri-bugfix.patch
  - ruby-1.6.6-900_XXX_strtod.patch
  - ruby-1.6.7-sux0rs.patch
  - ruby-1.6.7-libobj.patch

* Wed Jan 15 2003 Jens Petersen <petersen@redhat.com> 1.6.7-14
- rebuild to update tcltk deps

* Mon Dec 16 2002 Elliot Lee <sopwith@redhat.com> 1.6.7-13
- Remove ExcludeArch: x86_64
- Fix x86_64 ruby with long2int.patch (ruby was assuming that sizeof(long)
  == sizeof(int). The patch does not fix the source of the problem, just
  makes it a non-issue.)
- _smp_mflags

* Tue Dec 10 2002 Tim Powers <timp@redhat.com> 1.6.7-12
- rebuild to fix broken tcltk deps

* Tue Oct 22 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-11
- use %%configure macro instead of configure script.
- use the latest config.{sub,guess}.
- get archname from rbconfig.rb for %%dir
- applied some patches from Debian:
  - 801_extmk.rb-shellwords.patch: use Shellwords
  - 801_mkmf.rb-shellwords.patch: mkmf.rb creates bad Makefile. the Makefile
    links libruby.a to the target.
  - 803_sample-fix-shbang.patch: all sample codes should be
    s|/usr/local/bin|/usr/bin|g
  - 804_parse.y-new-bison.patch: fix syntax warning.
  - 805_uri-bugfix.patch: uri.rb could not handle correctly broken mailto-uri.
- add ExcludeArch x86_64 temporarily to fix Bug#74581. Right now ruby can't be
  built on x86_64.

* Tue Aug 27 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-10
- moved sitedir to /usr/lib/ruby/site_ruby again according as our perl and
  python.
- ruby-1.6.7-resolv1.patch, ruby-1.6.7-resolv2.patch: applied to fix 'Too many
  open files - "/etc/resolv.conf"' issue. (Bug#64830)

* Thu Jul 18 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-9
- add the owned directory.

* Fri Jul 12 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-8
- fix typo.

* Thu Jul 04 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-7
- removed the ruby-mode-xemacs because it's merged to the xemacs sumo.

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Wed Jun 19 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-5
- fix the stripped binary.
- use the appropriate macros.

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-3
- ruby-1.6.7-libobj.patch: applied to fix autoconf2.53 error.

* Mon Mar 18 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-2
- ruby-man-1.4.6-jp.tar.bz2: removed.
- ruby-refm-rdp-1.4.7-ja-html.tar.bz2: uses it instead of.
- ruby-1.6.7-500-marshal-proc.patch, ruby-1.6.7-501-class-var.patch:
  removed.
- ruby-1.6.7-100.patch: applied a bug fix patch.
  (ruby-dev#16274: patch for 'wm state')
  (PR#206ja: SEGV handle EXIT)
- ruby-1.6.7-101.patch: applied a bug fix patch.
  (ruby-list#34313: singleton should not be Marshal.dump'ed)
  (ruby-dev#16411: block local var)
- ruby-1.6.7-102.patch: applied a bug fix patch.
  (handling multibyte chars is partially broken)
- ruby-1.6.7-103.patch: applied a bug fix patch.
  (ruby-dev#16462: preserve reference for GC, but link should be cut)

* Fri Mar  8 2002 Akira TAGOH <tagoh@redhat.com> 1.6.7-1
- New upstream release.
- ruby-1.6.6-100.patch, ruby-1.6.6-501-ruby-mode.patch:
  removed. these patches no longer should be needed.
- ruby-1.6.7-500-marshal-proc.patch: applied a fix patch.
  (ruby-dev#16178: Marshal::dump should call Proc#call.)
- ruby-1.6.7-501-class-var.patch: applied a fix patch.
  (ruby-talk#35157: class vars broken in 1.6.7)

* Wed Feb 27 2002 Akira TAGOH <tagoh@redhat.com> 1.6.6-5
- Disable alpha because nothing is xemacs for alpha now.

* Tue Feb  5 2002 Akira TAGOH <tagoh@redhat.com> 1.6.6-3
- Fixed the duplicate files.

* Tue Feb  5 2002 Akira TAGOH <tagoh@redhat.com> 1.6.6-2
- Fixed the missing %%defattr

* Fri Feb  1 2002 Akira TAGOH <tagoh@redhat.com> 1.6.6-1
- New upstream release.
- Applied bug fix patches:
  - ruby-1.6.6-501-ruby-mode.patch: ruby-talk#30479: disables font-lock
    coloring.
  - ruby-1.6.6-100.patch: ruby-talk#30203: Ruby 1.6.6 bug and fix
                          ruby-list#33047: regex bug
                          PR#230: problem with -d in 1.6.6
- Added ruby-mode and ruby-mode-xemacs packages.
- Ruby works fine for ia64. so re-enable to build with ia64.
  (probably it should be worked for alpha)

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Jul 19 2001 Bernhard Rosenkraenzer <bero@redhat.com> 1.6.4-2
- Remove Japanese description and summaries; they belong in specspo and
  break rpm
- Clean up specfile
- Mark language specific files (README.jp) as such
- bzip2 sources
- rename the libruby package to ruby-libs for consistency
- Exclude ia64 (doesn't build - the code doesn't seem to be 64-bit clean
  [has been excluded on alpha forever])

* Tue Jul 17 2001 Akira TAGOH <tagoh@redhat.com> 1.6.4-1
- rebuild for Red Hat 7.2

* Mon Jun 04 2001 akira yamada <akira@vinelinux.org>
- upgrade to nwe upstream version 1.6.4.

* Mon Apr 02 2001 akira yamada <akira@vinelinux.org>
- applied patch:
  - fixed method cache bug. etc. (Patch103, Patch104)

* Tue Mar 27 2001 akira yamada <akira@vinelinux.org>
- applied patch:
  - fixed marshal for bignum bug.
  - fixed scope of constant variables bug.

* Tue Mar 20 2001 akira yamada <akira@vinelinux.org>
- upgraded to new upstream version 1.6.3.

* Fri Feb 09 2001 akira yamada <akira@vinelinux.org>
- fixed bad group for libruby.
- Applied patch: upgraded to cvs version (2001-02-08):
  fixed minor bugs.

* Thu Jan 18 2001 akira yamada <akira@vinelinux.org>
- Applied patch: upgraded to cvs version (2001-01-15):
  fixed minor bugs(e.g. ruby makes extention librares too large...).

* Wed Jan 10 2001 akira yamada <akira@vinelinux.org>
- Applied patch: upgraded to cvs version (2001-01-09):
  fixed minor bugs.

* Sat Dec 30 2000 akira yamada <akira@vinelinux.org>
- Applied bug fix patch.

* Mon Dec 25 2000 akira yamada <akira@vinelinux.org>
- Updated to new upstream version 1.6.2.

* Fri Dec 22 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000122019.patch, added ruby_cvs.2000122215.patch
  (upgraded ruby to latest cvs version, 1.6.2-preview4).

* Wed Dec 20 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000121413.patch, added ruby_cvs.2000122019.patch
  (upgraded ruby to latest cvs version).
- new package: libruby

* Thu Dec 14 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000101901.patch, added ruby_cvs.2000121413.patch
  (upgraded ruby to latest cvs version).
- Removed ruby-dev.11262.patch, ruby-dev.11265.patch,
  and ruby-dev.11268.patch (included into above patch).

* Sun Nov 12 2000 MACHINO, Satoshi <machino@vinelinux.org> 1.6.1-0vl9
- build on gcc-2.95.3

* Thu Oct 19 2000 akira yamada <akira@vinelinux.org>
- Added ruby-dev.11268.patch.
- Removed ruby_cvs.2000101117.patch and added ruby_cvs.2000101901.patch
  (upgraded ruby to latest cvs version).
- Added ruby-dev.11262.patch.
- Added ruby-dev.11265.patch.

* Wed Oct 11 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000100313.patch and added ruby_cvs.2000101117.patch
  (upgraded ruby to latest cvs version).

* Mon Oct 09 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000100313.patch and added ruby_cvs.2000100313.patch
  (upgraded ruby to latest cvs version).

* Tue Oct 03 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000100218.patch and added ruby_cvs.2000100313.patch
  (upgraded ruby to latest cvs version).

* Mon Oct 02 2000 akira yamada <akira@vinelinux.org>
- Removed ruby_cvs.2000092718.patch and added ruby_cvs.2000100218.patch
  (upgraded ruby to latest cvs version).

* Wed Sep 27 2000 akira yamada <akira@vinelinux.org>
- Updated to upstream version 1.6.1.
- Removed ruby_cvs.2000082901.patch and added ruby_cvs.2000092718.patch
  (upgraded ruby to latest cvs version).

* Tue Aug 29 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.6.
- removed ruby-dev.10123.patch(included into ruby-1.4.6).
- Added ruby_cvs.2000082901.patch(upgraded ruby to latest cvs version).

* Tue Jun 27 2000 akira yamada <akira@redhat.com>
- Updated manuals to version 1.4.5.

* Sun Jun 25 2000 akira yamada <akira@redhat.com>
- Added ruby-dev.10123.patch.

* Sat Jun 24 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.5.
- Removed ruby_cvs.2000062401.patch(included into ruby-1.4.5).

* Thu Jun 22 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.4(06/22/2000 CVS).
- Removed ruby-dev.10054.patch(included into ruby_cvs.patch).
- Renamed to ruby_cvs20000620.patch from ruby_cvs.patch.

* Tue Jun 20 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.4(06/20/2000 CVS).
- Removed ruby-list.23190.patch(included into ruby_cvs.patch).
- Added ruby-dev.10054.patch.

* Thu Jun 15 2000 akira yamada <akira@redhat.com>
- Updated to version 1.4.4(06/12/2000 CVS).
- Added manuals and FAQs.
- Split into ruby, ruby-devel, ruby-tcltk, ruby-docs, irb.

* Tue Jun 13 2000 Mitsuo Hamada <mhamada@redhat.com>
- Updated to version 1.4.4

* Wed Dec 08 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.4.3

* Mon Sep 20 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.4.2 (Sep 18)

* Fri Sep 17 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.4.2

* Tue Aug 17 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.4.0

* Fri Jul 23 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- 2nd release
- Updated to version 1.2.6(15 Jul 1999)
- striped %%{prefix}/bin/ruby

* Mon Jun 28 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.2.6(21 Jun 1999)

* Wed Apr 14 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.2.5

* Fri Apr 09 1999 Atsushi Yamagata <yamagata@plathome.co.jp>
- Updated to version 1.2.4

* Fri Dec 25 1998 Toru Hoshina <hoshina@best.com>
- Version up to 1.2 stable.

* Fri Nov 27 1998 Toru Hoshina <hoshina@best.com>
- Version up to 1.1c9.

* Thu Nov 19 1998 Toru Hoshina <hoshina@best.com>
- Version up to 1.1c8, however it appear short life :-P

* Fri Nov 13 1998 Toru Hoshina <hoshina@best.com>
- Version up.

* Tue Sep 22 1998 Toru Hoshina <hoshina@best.com>
- To make a libruby.so.

* Mon Sep 21 1998 Toru Hoshina <hoshina@best.com>
- Modified SPEC in order to install libruby.a so that it should be used by
  another ruby entention.
- 2nd release.

* Mon Mar 9 1998 Shoichi OZAWA <shoch@jsdi.or.jp>
- Added a powerPC arch part. Thanks, MURATA Nobuhiro <nob@makioka.y-min.or.jp>
