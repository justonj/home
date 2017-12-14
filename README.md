## Skeleton NLU Application

### Docker deploy instructions

This application depends on and inherits from the [NLU Core module](https://github.com/iAmPlus/nlu). It relies on the [NLU database image](https://github.com/iAmPlus/nlu-postgres-docker) to provide a wrapped blank database instance for data to be loaded.

#### Installing Docker locally

[Ubuntu](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/)
[OSX](https://www.docker.com/docker-mac)

#### Quay.io

Quay.io is our container repository. If you haven't used docker and Quay.io locally before, follow instructions [here|https://iamplus.atlassian.net/wiki/spaces/NE/pages/108958457/Docker+Setup] to authenticate.

#### Running locally with docker

Use a FRESH CHECKOUT of nlu and aneeda. Check them out under the same directory:

```
$PATH_TO_DEV_DIR/nlu
$PATH_TO_DEV_DIR/aneeda
```

*DO NOT try to check this out over prior working directories.* There is enough cached state left in the Git repo by prior (local) runs of the NLU and Aneeda that you will encounter all kinds of wild problems; it is *not an efficient use of time* to try to solve them. Please just use a FRESH checkout.

Ensure the env directory is populated with
    - nlu.env (nlu-specific environment)
    - aneeda.env (aneeda-specific environment)
    - postgres.env (env needed by the postgres image at launch)

Then:

```docker-compose build && docker-compose up```

docker-compose will bind the NLU to localhost:8080 and you may execute queries of form

```localhost:8080/query?user_id=somebody&text=what%27s%20new%20with%20adele```

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

or any other valid command on the PATH of the aneeda container

#### Running in Kubernetes

Use the env-appropriate deployment file and your own kubeconfig to launch the service to a cluster:

```kubectl --kubeconfig path/to/your/kubeconfig --namespace $NLU_NAMESPACE create -f deployments/$ENV/aneeda_$env.json```

### Troubleshooting

make sure supporting containers are up to date with

```docker-compose pull```

### Legacy deploy instructions

Confluence docs are [here|https://iamplus.atlassian.net/wiki/display/NE/NLU+build+process]
