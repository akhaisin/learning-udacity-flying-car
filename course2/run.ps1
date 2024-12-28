docker build -t fcnd-conda ..

# This allows you to run 'python backyard_flier.py --host=host.docker.internal' 
# and connect to the host machine FCND-Simulator
docker run -i -t -v .:/app/course2 `
    --add-host=host.docker.internal:host-gateway `
    fcnd-conda `
    /bin/bash -c "/opt/conda/envs/fcnd/bin/python ./course2/up_and_down.py --host=host.docker.internal"