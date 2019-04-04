# VDV-Backend

## Grabbing the code
```python
https://github.com/DimaDemyanov/gyma
```

## Environment
python version more than 3.6

## Setup requirements
```python
pip install ./Requirements.txt
```
Copy ```./setup.py``` to root level directory and run from there (from root level):
```python
pip install -e .
```
Detailed instruction: [Stack Overflow](https://stackoverflow.com/questions/6323860/sibling-package-imports/50193944#50193944)

## Running server
```python
python ./server.py --profile [ONE OF: dev, prod, elephant, local]
```

## Example
```python
pyhton ./server.py dev
```

will start at 
```python
http://0.0.0.0:4201/vdv/
```

if running on localhost then visit the page after the start: [http://127.0.0.1:4201/vdv/swagger-ui/](http://127.0.0.1:4201/vdv/swagger-ui/)

