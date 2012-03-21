# Checkout tools if it doesn't exist
mkdir -p /vagrant/firefox
ln -s /vagrant/firefox
cd firefox
rm -f build_firefox.sh
wget https://raw.github.com/translate/translate/master/tools/mozilla/build_firefox.sh
chmod +x build_firefox.sh
./build_firefox.sh af
rm build_firefox.sh
ln -s tools/translate/tools/mozilla/build_firefox.sh

# Things we need to do
# TODO
# Copy .hgrc file to the correct place and any other needed configurations e.g. Subversion and friends.  If none exist then use a default.
