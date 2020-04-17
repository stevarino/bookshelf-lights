# launcher script

echo "Updating this directory"
git pull

echo ""
echo "============================================="
echo "Updating python requirements"
pip3 install -r requirements.txt

echo ""
echo "============================================="
echo "Running lights"
python3 main.py

echo ""
echo "============================================="
echo "Rebooting"
# /sbin/reboot
