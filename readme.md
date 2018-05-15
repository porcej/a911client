# a911

A python module to act as a wrapper for Active911's XMPP interface.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This module is designed to work with `Python >=3.5`.  `Python 2` may work, your milage may very.  The `requirements.txt` file contains the required libraries.  

```
python >=  3.5
$pip install -r requirements.txt
```

### Usage

#### Using this module in your application

Import the Active911 class from the a911 module
```
from a911 import Active911
```

Build a child class of `Active911` that overides `Active911.alert(self, alert_id, alert_msg)` to process alerts as needed.

```
class Active911Client(Active911):
    """
    Here we override Active911 to implament a simple
    demonstration client
    - We are just going to pretty print the json to the screen
    """
    def alert(self, alert_id, alert_msg):
        """
        This is where we do somehting with the alert.
        This method should be implamented using the 
        """
        logging.info("Alert {}:\n\n{}\n".format(alert_id, json.dumps(alert_msg)))
```


Initilize the client with an Active911 device id and run client.run.  In most cases block should be set to True(defualt) unless the client is handling threading.  If the client is handling threading, keep a close eye on thread locking.

For most cases, a911, handles threading
```
    xmpp = Active911Client('XXXXXX-XXXX')
    xmpp.run()
```

For the case where the client handles threading
```
    xmpp = Active911Client('XXXXXX-XXXX')
    xmpp.run(block=False)
```


### Sample applicaitons

#### sample.py

The sample applicaiton, `sample.py` demonstrates using a911 to pretty print alert data to the screen.  

```
Usage: sample.py [options]

Options:
  -h, --help                show this help message and exit
  -q, --quiet               set logging to ERROR
  -d, --debug               set logging to DEBUG
  -v, --verbose             set logging to COMM
  -a AREG, --aid=AREG       Active911 Registration ID
```


#### samplefile.py
The example applicaiton, `samplefile.py` demonstrates using a911's Active911 class to save alert messages as json files in a predefined directory.

```
Usage: samplefile.py [options]

Options:
  -h, --help            show this help message and exit
  -q, --quiet           set logging to ERROR
  -d, --debug           set logging to DEBUG
  -v, --verbose         set logging to COMM
  -a AREG, --aid=AREG   Active911 Registration ID
  -p OPATH, --path=OPATH
                        Output directory
```


## Built With

* [Anaconda Python](https://conda.io/) - The python framework
* [SleekXMPP](https://github.com/fritzy/SleekXMPP) - XMPP Library
* [Requests](http://docs.python-requests.org/en/master/) - Request and session handling

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/porcej/cc71497a2b455f27bca8c879731e68dc) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/porcej/a911_bridge/tags). 

## Authors

* **Joseph Porcelli** - *Initial work* - [porcej](https://github.com/porcej)

See also the list of [contributors](https://github.com/porcej/a911_bridge/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

