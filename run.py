#!/usr/bin/env python
"""
Cortex Application Entry Point
Brain Research Methodology Platform
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.app import create_app
from app.logger import logger


def main():
    """Main entry point"""
    
    # Get configuration
    env = os.getenv('FLASK_ENV', 'development')
    port = int(os.getenv('PORT', 5050))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting Cortex application...")
    logger.info(f"Environment: {env}")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    
    # Create Flask app
    app = create_app()
    
    # Run the application
    try:
        if env == 'production':
            logger.info("Running in production mode")
            # In production, use WSGI server (gunicorn)
            # This is just for testing
            app.run(
                host=host,
                port=port,
                debug=False,
                threaded=True
            )
        else:
            logger.info("Running in development mode")
            app.run(
                host=host,
                port=port,
                debug=True,
                use_reloader=True,
                threaded=True
            )
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
