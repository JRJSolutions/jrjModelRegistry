export const apiCall = async ({ url, options }) => {
    try {
        options.headers = {
            ...options?.headers,
            "Content-Type": "application/json",
        };



        const responseRaw = await fetch(`/${url}`, {
            ...options,
        });

        const response = await responseRaw.json();
        return response;
    } catch (error) {
        return {
            error: true,
            errorMessage: error.message,
        };
    }
};


export const apiCallWithToken = async ({url, options}) => {


    const result = await apiCall({
        url,
        options: {
            ...options,
            headers: {
                ...options.headers,
                // authorization: `Bearer ${projectToken}`,
            },
        },
    });

    if (result.error) {
        console.error(result.error);
        // message.error("Server error.");
    }

    return result;
}