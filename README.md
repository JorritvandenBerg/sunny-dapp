# Sunny dApp
This repository contains a insurance smart contract that pays out based on a observed weather condition that can be signalled by an oracle. The decentralized application is build for the NEO blockchain using the Python tools (neo-boa and neo-pyton).

## Table of Contents

- [Disclaimer](#disclaimer)
- [Installation](#installation)
- [Usage](#usage)
- [Maintainer](#maintainer)
- [License](#license)

## Disclaimer
This smart contract is for experimenal purposes and requires rigorous testing before deployment on the Main Net.

## Installation

### Dependencies

1. Install GIT 
[GIT installation guide] (https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

2. Install Docker CE
[Docker CE installation guide] (https://docs.docker.com/engine/installation/)

3. To use Docker without sudo

``` bash
# Add your username to the Docker group
sudo usermod -aG docker $USER

# Logout and login again for this to take effect
logout
 ```

## Usage
To deploy the smart contract, it first needs to be set to the correct OWNER, which is a byte array of your hex script hash. Having done so, the script can be compiled with pip neo-boa and deployed with the neo-python container.

Having Docker installed, you could do it like this:

``` bash
# Clone the git repository
git clone https://github.com/JorritvandenBerg/sunny-dapp.git

# Go to the sunny_dapp directory
cd sunny-dapp

# Build the neo-boa docker-container
docker build -t neo-boa ./neo-boa

# Compile the sunny_dapp.py smart contract in the smartcontract directory
docker run -it -v /absolute/path/to/sunny_dapp/smartcontract:/python-contracts -v /absolute/path/to/sunny_dapp/smartcontract/compiled:/compiled-contracts neo-boa

# Check if there is a compiled .avm file in the smartcontract subdirectory
cd smartcontract

# Go back to the main directory
cd ..

# Build the neo-python docker container
docker build -t neo-python ./neo-python

# Run the neo-python Docker container
docker run -it -v /absolute/path/to/sunny_dap/smartcontract/compiled:/smartcontract neo-python

# Create or import a wallet
create wallet {/path}

# Import WIF of your OWNER address
import wif {wif}

# Import the contract (with storage enabled)
import contract /smartcontract/sunny_dapp.avm 0710 05 True

# Fill in the metadata form and optionally deploy with your wallet password after a succesful test invoke

# Wait a few minutes for deployment and grab the contract hash with
contract search <entered author name> 

 ```

## Maintainers

[@JorritvandenBerg](mailto:jorrit_van_den_berg@hotmail.com)

## License

[License](LICENSE)



