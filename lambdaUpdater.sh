#/usr/bin/bash

app=$0

usage() {
	echo "usage: $app -z ZIP_FILENAME -f LAMBDA_FUNCTION_NAME"
	echo "Note: All parameters are required"
	echo "Parameter ZIP_FILENAME does not need the .zip extension"
}

while getopts ":z:f:h" opt; do 
	case "$opt" in
		z)
			zipFileName=$2
		;;
		f)
			lambdaFunctionName=$4
		;;
		h)
			usage
	esac
done

if [ -z "$zipFileName" ] || [ -z "$lambdaFunctionName" ]; then
	usage
	exit
else
	echo "VSCode's workspace files and test folder will be excluded as they are not needed" 

	echo "Removing old $zipFileName.zip..."
	\rm -rf $zipFileName.zip

	echo "Creating the zip file with all the content in current directory..."
	zip -r $zipFileName.zip * -x *.code-workspace -x test*

	echo "Uploading the $zipFileName.zip to Lambda Function $lambdaFunctionName"
	aws lambda update-function-code --function-name $lambdaFunctionName --zip-file fileb://$zipFileName.zip

	echo "Done"
fi