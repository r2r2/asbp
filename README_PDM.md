
# Package manager PDM  
https://pdm.fming.dev/

###1. Recommended installation method:

<code>pip install --user pdm</code>

###2. Enable PEP 582 globally  
<code>eval "$(pdm --pep582)"</code>

###3. Install the packages pinned in lock file

<code>pdm install</code>

### Show what packages are installed
<p> list all packages installed in the packages directory:</p>
<code>pdm list</code>  

<code>pdm list --graph</code>

### Add dependencies
<code>pdm add sanic requests tortoise-orm</code>

### Update existing dependencies
<code>pdm update</code>

### Remove existing dependencies
<code>pdm remove requests</code>

### Export locked packages
<code>pdm list freeze > requirements.txt</code>  
or  
<code>pdm export -o requirements.txt</code>  
<br>
<br>
