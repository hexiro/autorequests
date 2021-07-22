# autorequests

Autorequests provides an easy way to create a simple API wrapper from request data generated by your browser.

![BUILT WITH SWAG](https://forthebadge.com/images/badges/built-with-swag.svg)
![NOT A BUG A FEATURE](https://forthebadge.com/images/badges/not-a-bug-a-feature.svg)
![IT WORKS. WHY?](https://forthebadge.com/images/badges/it-works-why.svg)

### Showcase

** the website shown in this example is [imperialb.in](https://imperialb.in)
![example showcase gif](https://i.imgur.com/75tMMIW.gif)

### Example Use Cases

* Creating a foundation for an API wrapper
* Recreating a request outside the browser
* Testing what cookies or headers are required for a server to understand your request

### ✂️ How to Copy

1. Inspect Element
2. Go to `Network` tab
3. Find web request
4. Right-Click
5. Copy
6. Choose A `Copying Method`:

### Supported Copying Methods

* Powershell
* Node.JS fetch

## 📦 Installation

install the package with pip

```
$ pip3 install autorequests
```

or download the latest development build from GitHub

```
$ pip3 install -U git+https://github.com/Hexiro/autorequests
```

## 🖥️ Command Line

```console
$ autorequests --help
```

directory options

```console
  -i, --input           Input Directory
  -o, --output          Output Directory
```

generation options

```
  --return-text         Makes the generated method's responses return .text instead of .json()
  --single-quote        Uses single quotes instead of double quotes
  --no-headers          Removes all headers from the operation
  --no-cookies          Removes all cookies from the operation
```

## 🚩 Known Issues

* Method names are parsed from the url, but if the URL doesn't have any paths with a valid method name, an invalid
  method name will be used.
* Sometimes when copying fetches from the browser, some important headers aren't including, causing the resulting API
  wrapper to fail requests.

## 📅 Planned Features

* detecting base paths (like /api/v1) and setting that in the class constructor. (maybe).

## 🐞 Contributing

This project has a lot of room for improvement in optimizing regexps, better OOP, and bug fixes. If you make an issue,
pr, or suggestion, it'll be very appreciated <3.