# uro
Using a URL list for security testing can be painful as there are a lot of URLs that have uninteresting/duplicate content; `uro` aims to solve that.

It doesn't make any http requests to the URLs and removes:
- human written content e.g. blog posts
- urls with same path but parameter value difference
- incremental urls e.g. `/cat/1/` and `/cat/2/`
- image, js, css and other static files

#### Usage
First, install uro with pip:
```
pip3 install uro
```
Now, there's just one way to use it, no args, no bullshit.
```
cat urls.txt | uro
```

![uro-demo](https://i.ibb.co/x2tWCC5/uro-demo.png)
