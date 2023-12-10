# This is the dev branch

This branch is for development of the next version of the project. It is not
stable and should not be used in production.

See the [main branch](https://github.com/ChristopherKlix/haw_ipj1_datacrunch/tree/main) for the current stable version.

## Project structure

The project is structured as follows:

```sh
.
├── public
│   ├── ...
├── src
│   ├── ...
├── Dockerfile
├── README.md
├── deploy.sh
├── requirements.txt
```

The `public` folder contains the deployable files for the webserver.
A GitHub action is used to automatically deploy the files to the `public` branch.

The `src` folder contains the source code for the project.
Changes are made here locally.
