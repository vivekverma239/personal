export NODE_OPTIONS=--max_old_space_size=4096
npm run-script build
aws s3 sync -r public/. s3://personal-website-vivek