## Skeleton NLU Application

### Docker deploy instructions

This application depends on and inherits from the [NLU Core module](https://github.com/iAmPlus/nlu). It relies on the [NLU database image](https://github.com/iAmPlus/nlu-postgres-docker) to provide a wrapped blank database instance for data to be loaded.

#### Installing Docker locally

[Ubuntu](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
[OSX](https://www.docker.com/docker-mac)

#### Quay.io

Quay.io is our container repository. If you haven't used docker and Quay.io locally before, follow instructions [here](https://iamplus.atlassian.net/wiki/spaces/NE/pages/108958457/Docker+Setup) to authenticate.

#### Running locally with docker

Use a FRESH CHECKOUT of the NLU core and this application. Check them out under the same directory:

```
$PATH_TO_DEV_DIR/nlu
$PATH_TO_DEV_DIR/ho
```

Ensure the env directory is populated with
    - nlu.env (nlu-specific environment)
    - ho.env (this-application-specific environment)
    - postgres.env (env needed by the postgres image at launch)

Then:

```docker-compose build && docker-compose up```

docker-compose will bind the NLU to localhost:8080 and you may execute queries of form

```localhost:8080/query?user_id=somebody&text=what%20time%20is%20it```

#### Applying a Code Change

The docker-compose.yml file is set up to re-run *make rebuild* on bringup. To apply a code change, just

```docker-compose down && docker-compose up```

The rebuild target will be run for you when the server is brought back up, and your code changes should be applied.

#### Running Tests

```docker-compose run nlu make test-nlu```

will create necessary containers, run tests within them, and output the test results

please note that with docker-compose run {container name} {command} the command will be passed through to the container, allowing specific tests to be run as:

e.g. to run just `type_manager_test.py`:

```docker-compose run nlu test/run -vv test/type_manager_test.py test```

or any other valid command on the PATH of this application's container

### Troubleshooting

make sure supporting containers are up to date with

```docker-compose pull```

### Legacy deploy instructions

Confluence docs are [here](https://iamplus.atlassian.net/wiki/display/NE/NLU+build+process)
