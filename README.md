# Project name

A short introduction to your project could go here. This README outlines the
details of collaborating on this Grow website.

## Prerequisites

At a minimum, you will need the following tools installed:

1. [Git](http://git-scm.com/)
2. [Grow](https://grow.io)

If you do not have Grow, you can install it using:

```
curl https://install.growsdk.org | bash
```

## Running the development server

Prior to starting the development server, you may have to install dependencies
used by your project. The `grow install` command walks you through this and
tries to set up your environment for you.

The `grow run` command starts your development server. You can make changes to
your project files and refresh to see them reflected immediately.

```
grow install
grow run
```

## Building

You can use the `grow build` command to build your whole site to the `build`
directory. This is a good way to test and verify the generated code.

```
grow build
```

## Kintaro

Grow has a basic integration with Kintaro. Some features are described below.

1. Visit https://kintaro-content-server.appspot.com to access Kintaro.
1. Observe the Kintaro preprocessor configuration in `podspec.yaml`. Control the integration (which collections are connected and which Kintaro repository and project are used).
1. Run `grow preprocess -p kintaro` to bind a Grow collection to a Kintaro collection.

## Staging

You can deploy a development server to App Engine. Stakeholders can edit in
Kintaro and see changes live in staging, on the development server.

1. Download the [Gcloud SDK](https://cloud.google.com/sdk/).
1. Create a new Gcloud project using `gcloud projects create` or use an existing one.
1. Create a new App Engine using `gcloud app create --project=<project>` or use an existing one.
1. Share your Kintaro collection with your App Engine app's service account (`appid@appspot.gserviceaccount.com`).
1. Deploy with the commands below.

```
make develop
make project=<project> deploy
```
