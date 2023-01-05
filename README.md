<img 
    style="display: block; 
           margin-left: auto;
           margin-right: auto;
           width: 96px;"
    src="https://git.obelus.online/Obelus_Admin/HotCompress/raw/commit/74a05e8868a26fbf88923e0d8d48656ef18edd4d/hotcompress.svg" 
    alt="Our logo">
</img>
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
