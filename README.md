# ujsrepack
Unpack a long JavaScript file (such as a user.js file) into seperate files/folders and repack the files back to the long .js file.

## `unpack.py`
### Usage: `unpack.py Yours.user.js`

`Yours.user.js` will be splitted to smaller files and folders with names starting with `@`. Each function will be put in a seperate file and any sub-function of a function will be put in the folder named by the function (and so as the sub-fucntions of the sub-function). The out-most function will be named as "main" by default. Any lines before the main function in `Yours.user.js` will be put in the `@preface.js`.

## `repack.py`
### Usage: `repack.py Yours.user.js`

`repack.py` will search for files whose names start with `@` and pack them back into `Yours.user.js` if the corresponding functions are mentioned in `@main.js`.
