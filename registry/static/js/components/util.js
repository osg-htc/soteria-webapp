/**
 * Used to process input options of a component
 *
 * Allows options to be built with data not yet decided
 *
 * @param options A function that takes input data or an object to be combined with input data
 * @param data - Extra data to be added later by child
 */
export function buildOptions(options, data){
    if(options instanceof Function){
        return options(data)
    } else {
        return {...options, ...data}
    }
}