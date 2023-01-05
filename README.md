<div style="text-align: center;">
![logo of towel with steam being emitted](./hotcompress.svg)
</div>

## What is This?
Hot Compress is an application which allows the storage of files in a database. Although this is typically a bad idea, it may work as a local download catalogue to prevent duplication of files acquired over many years.

## Usage
Hot Compress is currently a command line utility, usage is as follows.

Compress and store files:
`python hc.py file1.ext file2.ext`

Get a lis of files with indexes from the database
`python hc.py [list|LIST|print|PRINT]`

Extract Files by Index
`python hc.py 2`

## Known Issues
It's currently not possible to store files with only a number as the name (Why would you want to?)
