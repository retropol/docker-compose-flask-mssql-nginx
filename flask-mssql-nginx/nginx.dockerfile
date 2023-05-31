# Use a base image with Nginx installed
FROM nginx:latest

# Copy the custom nginx.conf file to the container
COPY nginx.conf /etc/nginx/nginx.conf



# Expose the ports that Nginx will listen on (usually 80 for HTTP and 443 for HTTPS)
EXPOSE 80
EXPOSE 443

# Start Nginx when the container starts
CMD ["nginx", "-g", "daemon off;"]