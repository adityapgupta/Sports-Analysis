let canvasdata: ImageData;
const draw = function(cvs: HTMLCanvasElement, ctx: CanvasRenderingContext2D) {
    let cvrect = cvs.getBoundingClientRect()
    let cw = cvrect.width
    let ch = cvrect.height
    ctx.clearRect(0, 0, cw, ch)
    ctx.lineWidth = 3
    ctx.beginPath()
    ctx.rect(Math.floor(cw/6), Math.floor(ch/4), Math.floor(cw/4), Math.floor(ch/3))
    ctx.stroke()
    // canvasdata = ctx.getImageData(0, 0, cw, ch)
    console.log(`redrew to ${[cw, ch]}`)
}

class box {
    x: number
    y: number
    w: number
    h: number
    color: string

    constructor(x:number, y:number, w:number, h:number) {
        this.x = x
        this.y = y
        this.w = w
        this.h = h 
        this.color = "black"
    }

    transformed_coords(natural: [number, number], cvs:HTMLCanvasElement) {
        // transform the bounding box since the display size is different to the actual size
        let bbox = cvs.getBoundingClientRect()
        let wt = bbox.width/natural[0]
        let ht = bbox.height/natural[1]
        return [this.x * wt, this.y * ht, this.w * wt, this.y * ht]
    }

    draw(ctx: CanvasRenderingContext2D) {
        ctx.beginPath()
        ctx.strokeStyle = this.color
        ctx.rect(this.x, this.y, this.w, this.h)
    }
}

export { draw, canvasdata, box }