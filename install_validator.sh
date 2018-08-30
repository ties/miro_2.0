#!/bin/bash
if $(systemctl is-active --quiet postgresql); then
	echo "Postgres is active, installation can continue."
else
	echo "ERROR: PostgreSQL service not active, please activate and try again."
	exit
fi


DB_USER="miro";
DB_PWD="rpki";
DB_NAME="mirodb";
DB_FILEPATH="validator/db_provisioning/";

V_LOCAL_CONF="validator/conf/"
V_LOCAL_BIN="validator/bin/"
LOCAL_TAL="validator/conf/tals/";
LOCAL_PREFETCH="validator/conf/prefetch/";

CONF_DIR="/etc/miro/"
DATA_DIR="/var/lib/miro/"
TAL_DIR="/etc/miro/tals/"
PREFETCH_DIR="/etc/miro/prefetch/"
EXPORT_DIR="/var/lib/miro/export/"
BASE_DIR="/var/lib/miro/repo/"

MIRO_VALIDATOR_JAR_DIR="/opt/miro_validator/"
MIRO_BROWSER_DIR="/opt/miro_browser/"
LOCAL_MIRO_VALIDATOR_JARNAME="MIRO.Validator-0.0.2-SNAPSHOT-jar-with-dependencies.jar"
MIRO_VALIDATOR_JARNAME="miro_validator.jar"


if [ -z "${JAVA_HOME}" ]
then
	echo "JAVA_HOME not set, exiting!"
	exit
else
	JAVA_HOME=${JAVA_HOME};
fi

if ! grep -q miro /etc/group
then
	sudo adduser $DB_USER --gecos "First Last,RoomNumber,WorkPhone,HomePhone" --disabled-password
fi


sudo -u postgres createuser $DB_USER;
sudo -u postgres createdb $DB_NAME;
sudo -u postgres psql -c "alter user $DB_USER with encrypted password '$DB_PWD';"
sudo -u postgres psql -c "grant all privileges on database $DB_NAME to $DB_USER ;"
sudo -u miro psql -d mirodb -f $DB_FILEPATH"roaprefix.sql"
sudo -u miro psql -d mirodb -f $DB_FILEPATH"create_tables.sql"


# Create dirs
for dir in $CONF_DIR $DATA_DIR $TAL_DIR $PREFETCH_DIR $EXPORT_DIR $BASE_DIR $MIRO_VALIDATOR_JAR_DIR
do
	if [ ! -d "$dir" ]; then
		echo $dir;
		mkdir $dir;
	fi
done

# Move config files
cp $V_LOCAL_CONF"miro.conf" $CONF_DIR;
cp -r "$LOCAL_TAL"* $TAL_DIR;
cp "$LOCAL_PREFETCH"* $PREFETCH_DIR;

# Move jar
cp "$V_LOCAL_BIN""$LOCAL_MIRO_VALIDATOR_JARNAME" "$MIRO_VALIDATOR_JAR_DIR""$MIRO_VALIDATOR_JARNAME";

# Give right to miro user
sudo chown -R miro:miro $CONF_DIR;
sudo chown -R miro:miro $DATA_DIR;
sudo chown -R miro:miro $MIRO_VALIDATOR_JAR_DIR;

# Set JAVA_HOME in systemd file
sed -i "s'JAVA_HOME'${JAVA_HOME}'g" "$V_LOCAL_CONF""systemd/miro_validator.service";

# Install services
cp "$V_LOCAL_CONF""systemd/miro_validator.service" /etc/systemd/system;
cp "$V_LOCAL_CONF""systemd/miro_validator.timer" /etc/systemd/system;
systemctl start miro_validator.timer
systemctl enable miro_validator.timer



