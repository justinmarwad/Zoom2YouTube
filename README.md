## Zoom2YouTube - A Project To Save You Time ## 

Zoom2YouTube brings together a few different projects and provides you with an easy project that lets you download recorded Zoom meetings, edit a logo into them, and upload them to YouTube directly. 

### Latest Update Notes ### 

I'm happy to announce that I've updated this project to fix automatic Zoom downloads! You will need to create a server-to-server OAuth app in Zoom and then add the account ID, client ID, and client secret to the .env file. Additionally, I had to make sure that in the code I created an account authentication vs client authentication. You don't have to worry about that though. 

I'll update the documentation in my next update to give instructions on how to create a server-to-server OAuth app in Zoom. You should be able to Google it (or Bing Chat it!) for now and be fine though. The next update on my pipeline is to enable automatic YouTube uploads. I made some progress here and added in a new library, but I will need to figure out automatic OAuth authentication for this (right now that would have to be done manually, which would prevent this script from being run automatically).  

### Documentation ###

TBD

### CREDITS ###

Makes use of the following two projects: 

1. Zoom Meeting Downloader: https://github.com/tribloom/Zoom-Meeting-Download
2. YouTube  Uploader: https://github.com/porjo/youtubeuploader

### LICENSE ##

MIT License

Copyright (c) 2023 Justin Marwad

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
