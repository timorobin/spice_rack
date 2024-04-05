# spice_rack
A collection of building blocks for doing standard things that I use in other projects. A lot of this is just 
personal preference, and serves merely to prevent me from rewriting common pieces of functionality.

Fully typed and heavily reliant on pydantic v2.

Some of the subpackages
=======================

See their individual docs for more info.

bases
-----
Extensions on pydantic's BaseModel for common use-cases such as an immutable class, or a class that 
is meant to be dispatched, so we can easily build polymorphic families of classes and hook into pydantic's validation
framework.

Also contains a base class extending the stdlib str class that hooks into pydantic's validation framework. Helpful or 
improving type annotations and ensuring things like keys have standardized formatting.

fs_ops
------
File and directory objects that aim to abstract away the underlying file-system, which means you can do the same 
stuff with a FilePath instance regardless of if the path is on s3, gcs or local. Some other stuff there too
regarding deferred file paths which means you can set a path as relative to an environment variable 
and evaluate it to a real FilePath or DirPath at some point in your control flow. Right now we only support 
local, gcs, and sftp, but s3 soon. 

logging
-------
Wrapper around loguru with some opinionated formatting. There are pydantic models for configuring the sinks,
and custom logger class that does some formatting for you and helps with structured data.

polars service
--------------
Polars DataFrame and LazyFrame type annotations meant to integrate with pydantic's validation system, meaning
I can set them as attributes on pydantic models without pydantic seeing them as 'arbitrary types'

ts service
----------
Simplifies date-related functionality. The primary class is a subclass of int that represents epoch milliseconds.
Main concept is to help with common gotchas and annoyances with dates, but this is a tough area. 
Likely not that useful at the moment.

gcp_auth
--------
Helps with indicating the credentials for different gcp services. There's a lot of different ways to authenticate 
to GCP, and they are very helpful in getting creds from the environment, but this can make it even more confusing. 
I use to be declarative in how I'm authenticating and which creds I am using, without losing the convenience of 
Google's helpers.



Installation
============
`pip install spice_rack[all]`
there are no optional/extra dependencies, so `pip install spice_rack[all]` is the same `pip install spice_rack` at the moment

Links
=====

[Docs](https://timorobin.github.io/spice_rack/)

[PyPI](https://pypi.org/project/spice-rack/)

[GitHub](https://github.com/timorobin/spice_rack)
